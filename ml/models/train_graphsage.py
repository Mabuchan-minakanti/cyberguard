from pathlib import Path
import sys

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)

# Allow imports from ml/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(
    str(PROJECT_ROOT / "ml")
)

from graphs.graph_dataset import build_temporal_graphs
from models.graph_utils import (
    fit_edge_scaler,
    transform_graphs,
)
from models.graphsage import (
    GraphSAGEEdgeClassifier,
)


DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

EPOCHS = 20
LEARNING_RATE = 0.001
WEIGHT_DECAY = 1e-4


def calculate_metrics(y_true, probabilities):

    predictions = (
        probabilities >= 0.5
    ).astype(int)

    accuracy = accuracy_score(
        y_true,
        predictions
    )

    precision = precision_score(
        y_true,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        predictions,
        zero_division=0
    )

    try:
        roc_auc = roc_auc_score(
            y_true,
            probabilities
        )
    except ValueError:
        roc_auc = 0.0

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1]
    ).ravel()

    fpr = (
        fp / (fp + tn)
        if (fp + tn) > 0
        else 0.0
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
        "fpr": fpr,
    }


def run_epoch(
    model,
    graphs,
    criterion,
    optimizer=None
):

    training = optimizer is not None

    if training:
        model.train()
    else:
        model.eval()

    all_labels = []
    all_probabilities = []

    total_loss = 0.0

    for graph in graphs:

        graph = graph.to(DEVICE)

        if training:
            optimizer.zero_grad()

        with torch.set_grad_enabled(training):

            logits = model(
                graph.x,
                graph.edge_index,
                graph.edge_attr
            )

            loss = criterion(
                logits,
                graph.y.float()
            )

            if training:
                loss.backward()

                optimizer.step()

        probabilities = torch.sigmoid(
            logits
        )

        total_loss += (
            loss.item()
            * graph.y.numel()
        )

        all_labels.extend(
            graph.y.detach()
            .cpu()
            .numpy()
            .tolist()
        )

        all_probabilities.extend(
            probabilities.detach()
            .cpu()
            .numpy()
            .tolist()
        )

    all_labels = np.array(
        all_labels
    )

    all_probabilities = np.array(
        all_probabilities
    )

    metrics = calculate_metrics(
        all_labels,
        all_probabilities
    )

    metrics["loss"] = (
        total_loss / len(all_labels)
    )

    return metrics


def main():

    print("=" * 50)
    print("GRAPH SAGE THREAT DETECTION")
    print("=" * 50)

    print(f"\nDevice: {DEVICE}")

    # --------------------------------------------------
    # Load temporal graphs
    # --------------------------------------------------

    print("\nLoading training graphs...")

    train_graphs = build_temporal_graphs(
        "UNSW_NB15_graph_train.csv"
    )

    print("\nLoading validation graphs...")

    val_graphs = build_temporal_graphs(
        "UNSW_NB15_graph_val.csv"
    )

    print("\nLoading test graphs...")

    test_graphs = build_temporal_graphs(
        "UNSW_NB15_graph_test.csv"
    )

    # --------------------------------------------------
    # Scale edge features
    # --------------------------------------------------

    print("\nFitting edge-feature scaler...")

    scaler = fit_edge_scaler(
        train_graphs
    )

    train_graphs = transform_graphs(
        train_graphs,
        scaler
    )

    val_graphs = transform_graphs(
        val_graphs,
        scaler
    )

    test_graphs = transform_graphs(
        test_graphs,
        scaler
    )

    # --------------------------------------------------
    # Create model
    # --------------------------------------------------

    model = GraphSAGEEdgeClassifier(
        node_features=4,
        edge_features=15,
        hidden_channels=64,
        dropout=0.2
    ).to(DEVICE)

    print("\nModel:")
    print(model)

    # --------------------------------------------------
    # Class imbalance
    # --------------------------------------------------

    train_labels = np.concatenate(
        [
            graph.y.numpy()
            for graph in train_graphs
        ]
    )

    normal_count = np.sum(
        train_labels == 0
    )

    attack_count = np.sum(
        train_labels == 1
    )

    positive_weight = (
        normal_count / attack_count
    )

    print("\nTraining labels:")
    print(f"Normal: {normal_count:,}")
    print(f"Attack: {attack_count:,}")
    print(
        f"Positive class weight: "
        f"{positive_weight:.4f}"
    )

    criterion = nn.BCEWithLogitsLoss(
        pos_weight=torch.tensor(
            positive_weight,
            dtype=torch.float32,
            device=DEVICE
        )
    )

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY
    )

    # --------------------------------------------------
    # Training
    # --------------------------------------------------

    best_f1 = -1.0
    best_state = None

    print("\nStarting training...\n")

    for epoch in range(
        1,
        EPOCHS + 1
    ):

        train_metrics = run_epoch(
            model,
            train_graphs,
            criterion,
            optimizer
        )

        val_metrics = run_epoch(
            model,
            val_graphs,
            criterion
        )

        print(
            f"Epoch {epoch:02d}/{EPOCHS} | "
            f"Train Loss: {train_metrics['loss']:.4f} | "
            f"Train F1: {train_metrics['f1']:.4f} | "
            f"Val Loss: {val_metrics['loss']:.4f} | "
            f"Val F1: {val_metrics['f1']:.4f} | "
            f"Val Recall: {val_metrics['recall']:.4f} | "
            f"Val ROC-AUC: {val_metrics['roc_auc']:.4f}"
        )

        if val_metrics["f1"] > best_f1:

            best_f1 = val_metrics["f1"]

            best_state = {
                key: value.cpu().clone()
                for key, value
                in model.state_dict().items()
            }

    # --------------------------------------------------
    # Restore best validation model
    # --------------------------------------------------

    if best_state is not None:

        model.load_state_dict(
            best_state
        )

    # --------------------------------------------------
    # Final test evaluation
    # --------------------------------------------------

    print("\n" + "=" * 50)
    print("FINAL TEST RESULTS")
    print("=" * 50)

    test_metrics = run_epoch(
        model,
        test_graphs,
        criterion
    )

    for name, value in test_metrics.items():

        print(
            f"{name.upper():10s}: "
            f"{value:.4f}"
        )

    # --------------------------------------------------
    # Save model
    # --------------------------------------------------

    model_dir = (
        PROJECT_ROOT
        / "ml"
        / "models"
        / "artifacts"
    )

    model_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    model_path = (
        model_dir
        / "graphsage_baseline.pt"
    )

    torch.save(
        {
            "model_state_dict":
                model.state_dict(),

            "node_features": 4,

            "edge_features": 15,

            "hidden_channels": 64,

            "best_validation_f1":
                best_f1,
        },
        model_path
    )

    print(
        f"\nModel saved to:\n"
        f"{model_path}"
    )

    print("\n" + "=" * 50)
    print("TRAINING COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    main()