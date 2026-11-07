from pathlib import Path
from io import BytesIO
import sys
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd
import torch
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from torch_geometric.data import Data

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ml.models.graphsage import GraphSAGEEdgeClassifier

MODEL_PATH = ROOT / "ml" / "models" / "artifacts" / "graphsage_baseline.pt"
SCALER_PATH = ROOT / "ml" / "models" / "artifacts" / "edge_scaler.joblib"

EDGE_FEATURES = [
    "flow_count", "dur", "sbytes", "dbytes", "Spkts", "Dpkts",
    "Sload", "Dload", "sloss", "dloss", "Sjit", "Djit",
    "tcprtt", "synack", "ackdat"
]

MAX_UPLOAD_BYTES = 100 * 1024 * 1024

app = FastAPI(
    title="GraphSAGE Cyber Threat Detection API",
    description="Graph-based network edge threat scoring using a trained GraphSAGE model.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = None
scaler = None
checkpoint_info = {}
load_error = None


class EdgeInput(BaseModel):
    src_node: int = Field(ge=0)
    dst_node: int = Field(ge=0)
    features: Dict[str, float]


class PredictRequest(BaseModel):
    edges: List[EdgeInput] = Field(min_length=1, max_length=10000)
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)


def load_artifacts():
    global model, scaler, checkpoint_info, load_error

    try:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model checkpoint not found: {MODEL_PATH}")
        if not SCALER_PATH.exists():
            raise FileNotFoundError(f"Scaler not found: {SCALER_PATH}")

        checkpoint = torch.load(
            MODEL_PATH, map_location=device, weights_only=False
        )

        model_instance = GraphSAGEEdgeClassifier(
            node_features=int(checkpoint["node_features"]),
            edge_features=int(checkpoint["edge_features"]),
            hidden_channels=int(checkpoint["hidden_channels"]),
        )
        model_instance.load_state_dict(checkpoint["model_state_dict"])
        model_instance.to(device)
        model_instance.eval()

        scaler_instance = joblib.load(SCALER_PATH)

        if scaler_instance.n_features_in_ != len(EDGE_FEATURES):
            raise ValueError(
                f"Scaler expects {scaler_instance.n_features_in_} features; "
                f"expected {len(EDGE_FEATURES)}."
            )

        model = model_instance
        scaler = scaler_instance
        checkpoint_info = {
            "node_features": int(checkpoint["node_features"]),
            "edge_features": int(checkpoint["edge_features"]),
            "hidden_channels": int(checkpoint["hidden_channels"]),
            "best_validation_f1": float(checkpoint["best_validation_f1"]),
        }
        load_error = None

    except Exception as exc:
        model = None
        scaler = None
        load_error = f"{type(exc).__name__}: {exc}"


load_artifacts()


def ensure_model_ready():
    if model is None or scaler is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model artifacts are not ready: {load_error}",
        )


def predict_graph(src, dst, raw_features):
    """
    Build one temporal graph using the same node-feature construction
    as ml/graphs/graph_dataset.py, then score its edges.
    Self-loops are deliberately preserved.
    """
    src = np.asarray(src, dtype=np.int64)
    dst = np.asarray(dst, dtype=np.int64)
    raw_features = np.asarray(raw_features, dtype=np.float64)

    if len(src) == 0:
        raise ValueError("Cannot predict an empty graph.")

    if np.any(src < 0) or np.any(dst < 0):
        raise ValueError("Node IDs cannot be negative.")

    if not np.all(np.isfinite(raw_features)):
        raise ValueError("Edge features contain non-finite values.")

    scaled_features = scaler.transform(raw_features).astype(np.float32)

    # Match create_graph() in graph_dataset.py exactly.
    num_nodes = int(max(src.max(), dst.max())) + 1
    node_features = np.zeros((num_nodes, 4), dtype=np.float32)

    flow_counts = raw_features[:, 0].astype(np.float32)

    for source, target, flow_count in zip(src, dst, flow_counts):
        node_features[source, 0] += 1.0
        node_features[target, 1] += 1.0
        node_features[source, 2] += flow_count
        node_features[target, 3] += flow_count

    graph = Data(
        x=torch.tensor(node_features, dtype=torch.float32, device=device),
        edge_index=torch.tensor(
            np.vstack([src, dst]), dtype=torch.long, device=device
        ),
        edge_attr=torch.tensor(
            scaled_features, dtype=torch.float32, device=device
        ),
        num_nodes=num_nodes,
    )

    with torch.no_grad():
        logits = model(graph.x, graph.edge_index, graph.edge_attr)
        probabilities = (
            torch.sigmoid(logits).reshape(-1).cpu().numpy()
        )

    return probabilities


@app.get("/")
def root():
    return {
        "message": "GraphSAGE Cyber Threat Detection API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {
        "status": "ok" if model is not None and scaler is not None else "not_ready",
        "model_loaded": model is not None,
        "scaler_loaded": scaler is not None,
        "device": str(device),
        "error": load_error,
    }


@app.get("/model-info")
def model_info():
    return {
        "model_type": "GraphSAGEEdgeClassifier",
        "checkpoint": str(MODEL_PATH),
        "scaler": str(SCALER_PATH),
        "edge_feature_order": EDGE_FEATURES,
        "metadata": checkpoint_info,
        "device": str(device),
    }


@app.post("/predict")
def predict(request: PredictRequest):
    ensure_model_ready()

    try:
        src = np.asarray(
            [edge.src_node for edge in request.edges], dtype=np.int64
        )
        dst = np.asarray(
            [edge.dst_node for edge in request.edges], dtype=np.int64
        )

        raw_features = []

        for index, edge in enumerate(request.edges):
            missing = [
                name for name in EDGE_FEATURES
                if name not in edge.features
            ]
            if missing:
                raise HTTPException(
                    status_code=422,
                    detail=f"Edge {index} is missing features: {missing}",
                )

            values = [edge.features[name] for name in EDGE_FEATURES]

            if not np.all(np.isfinite(values)):
                raise HTTPException(
                    status_code=422,
                    detail=f"Edge {index} contains non-finite feature values.",
                )

            raw_features.append(values)

        probabilities = predict_graph(src, dst, raw_features)

        results = []
        for index, probability in enumerate(probabilities):
            score = float(probability)
            results.append({
                "edge_index": index,
                "src_node": int(src[index]),
                "dst_node": int(dst[index]),
                "threat_probability": round(score, 6),
                "prediction": (
                    "attack" if score >= request.threshold else "normal"
                ),
                "threshold": request.threshold,
            })

        attack_count = sum(
            item["prediction"] == "attack" for item in results
        )

        return {
            "edges_scored": len(results),
            "predicted_attacks": attack_count,
            "predicted_normal": len(results) - attack_count,
            "threshold": request.threshold,
            "results": results,
            "note": "Scores apply to the supplied graph snapshot. "
                    "Probabilities are model scores and may not be calibrated.",
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {type(exc).__name__}: {exc}",
        ) from exc


@app.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    threshold: float = Query(default=0.5, ge=0.0, le=1.0),
    result_limit: int = Query(default=1000, ge=1, le=10000),
):
    """
    Upload an already aggregated graph-edge CSV.
    Each time_window is processed as a separate graph.
    The label column is never passed to the model.
    """
    ensure_model_ready()

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file.",
        )

    try:
        content = await file.read()

        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail="File is too large. Maximum upload size is 100 MB.",
            )

        df = pd.read_csv(BytesIO(content))

        required_columns = [
            "time_window", "src_node", "dst_node", *EDGE_FEATURES
        ]

        missing_columns = [
            column for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "This CSV does not match the graph-edge format.",
                    "missing_columns": missing_columns,
                    "expected_features": required_columns,
                },
            )

        if df.empty:
            raise HTTPException(
                status_code=422,
                detail="The CSV contains no data rows.",
            )

        numeric_columns = [
            "time_window", "src_node", "dst_node", *EDGE_FEATURES
        ]

        for column in numeric_columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

            values = df[column].to_numpy(dtype=np.float64)

            if not np.all(np.isfinite(values)):
                raise HTTPException(
                    status_code=422,
                    detail=f"Column '{column}' contains missing or non-numeric values.",
                )

        for column in ["time_window", "src_node", "dst_node"]:
            values = df[column].to_numpy(dtype=np.float64)

            if np.any(values < 0) or not np.all(values == np.floor(values)):
                raise HTTPException(
                    status_code=422,
                    detail=f"Column '{column}' must contain non-negative integers.",
                )

            df[column] = df[column].astype(np.int64)

        df["_row_index"] = np.arange(len(df))

        all_results = []
        window_summaries = []

        total_attacks = 0
        total_normal = 0

        # Match build_temporal_graphs(): one graph per time_window.
        grouped = df.groupby("time_window", sort=True)

        for time_window, window_df in grouped:
            window_df = window_df.reset_index(drop=True)

            src = window_df["src_node"].to_numpy(dtype=np.int64)
            dst = window_df["dst_node"].to_numpy(dtype=np.int64)

            raw_features = window_df[EDGE_FEATURES].to_numpy(
                dtype=np.float64
            )

            probabilities = predict_graph(src, dst, raw_features)

            window_attacks = 0

            for local_index, probability in enumerate(probabilities):
                score = float(probability)
                is_attack = score >= threshold

                if is_attack:
                    window_attacks += 1

                result = {
                    "row_index": int(window_df.loc[local_index, "_row_index"]),
                    "time_window": int(time_window),
                    "src_node": int(src[local_index]),
                    "dst_node": int(dst[local_index]),
                    "threat_probability": round(score, 6),
                    "prediction": "attack" if is_attack else "normal",
                }

                if "srcip" in window_df.columns:
                    result["srcip"] = str(window_df.loc[local_index, "srcip"])

                if "dstip" in window_df.columns:
                    result["dstip"] = str(window_df.loc[local_index, "dstip"])

                all_results.append(result)

            window_edges = len(probabilities)
            window_normal = window_edges - window_attacks

            total_attacks += window_attacks
            total_normal += window_normal

            window_summaries.append({
                "time_window": int(time_window),
                "edges_scored": window_edges,
                "predicted_attacks": window_attacks,
                "predicted_normal": window_normal,
            })

        # Return the highest-risk edges first to keep the response manageable.
        all_results.sort(
            key=lambda item: item["threat_probability"],
            reverse=True,
        )

        returned_results = all_results[:result_limit]

        return {
            "filename": file.filename,
            "status": "completed",
            "total_edges": len(df),
            "total_windows": len(window_summaries),
            "predicted_attacks": total_attacks,
            "predicted_normal": total_normal,
            "attack_percentage": round(
                total_attacks / len(df) * 100, 2
            ),
            "threshold": threshold,
            "returned_results": len(returned_results),
            "result_limit": result_limit,
            "results_truncated": len(all_results) > result_limit,
            "results": returned_results,
            "windows": window_summaries,
            "label_column_used_for_prediction": False,
            "note": (
                "Each time window was processed as a separate graph. "
                "The CSV label column, if present, was excluded from model inputs. "
                "Probabilities are model scores and may not be calibrated."
            ),
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"CSV analysis failed: {type(exc).__name__}: {exc}",
        ) from exc

    finally:
        await file.close()
