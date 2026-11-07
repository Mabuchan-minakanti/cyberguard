from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)


# ============================================================
# Project paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"


# ============================================================
# Same edge features used by GraphSAGE
# ============================================================

FEATURES = [
    "flow_count",
    "dur",
    "sbytes",
    "dbytes",
    "Spkts",
    "Dpkts",
    "Sload",
    "Dload",
    "sloss",
    "dloss",
    "Sjit",
    "Djit",
    "tcprtt",
    "synack",
    "ackdat",
]


# ============================================================
# Load dataset
# ============================================================

def load_data(filename):
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{path}"
        )

    return pd.read_csv(path)


# ============================================================
# Evaluation
# ============================================================

def evaluate(model, X, y):
    probabilities = model.predict_proba(X)[:, 1]

    predictions = (probabilities >= 0.5).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y,
        predictions,
        labels=[0, 1]
    ).ravel()

    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    metrics = {
        "accuracy": accuracy_score(y, predictions),
        "precision": precision_score(
            y,
            predictions,
            zero_division=0
        ),
        "recall": recall_score(
            y,
            predictions,
            zero_division=0
        ),
        "f1": f1_score(
            y,
            predictions,
            zero_division=0
        ),
        "roc_auc": roc_auc_score(
            y,
            probabilities
        ),
        "fpr": fpr,
    }

    return metrics


# ============================================================
# Pretty print metrics
# ============================================================

def print_metrics(name, metrics):

    print()
    print("=" * 60)
    print(name)
    print("=" * 60)

    print(f"Accuracy : {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall   : {metrics['recall']:.4f}")
    print(f"F1 Score : {metrics['f1']:.4f}")
    print(f"ROC-AUC  : {metrics['roc_auc']:.4f}")
    print(f"FPR      : {metrics['fpr']:.4f}")


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 60)
    print("LOGISTIC REGRESSION BASELINE")
    print("=" * 60)

    # --------------------------------------------------------
    # Load temporal graph splits
    # --------------------------------------------------------

    print("\nLoading datasets...")

    train = load_data(
        "UNSW_NB15_graph_train.csv"
    )

    val = load_data(
        "UNSW_NB15_graph_val.csv"
    )

    test = load_data(
        "UNSW_NB15_graph_test.csv"
    )

    print(f"Train shape: {train.shape}")
    print(f"Val shape  : {val.shape}")
    print(f"Test shape : {test.shape}")

    # --------------------------------------------------------
    # Extract features and labels
    # --------------------------------------------------------

    X_train = train[FEATURES].values
    y_train = train["label"].values

    X_val = val[FEATURES].values
    y_val = val["label"].values

    X_test = test[FEATURES].values
    y_test = test["label"].values

    print("\nFeature shape:")
    print(f"X_train: {X_train.shape}")
    print(f"X_val  : {X_val.shape}")
    print(f"X_test : {X_test.shape}")

    # --------------------------------------------------------
    # Check class distribution
    # --------------------------------------------------------

    print("\nTraining label distribution:")
    print(pd.Series(y_train).value_counts().sort_index())

    # --------------------------------------------------------
    # StandardScaler
    #
    # IMPORTANT:
    # Fit ONLY on training data.
    # --------------------------------------------------------

    print("\nScaling features...")

    scaler = StandardScaler()

    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    X_test = scaler.transform(X_test)

    # --------------------------------------------------------
    # Logistic Regression
    #
    # class_weight='balanced' handles class imbalance.
    # --------------------------------------------------------

    print("\nTraining Logistic Regression...")

    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42,
    )

    model.fit(X_train, y_train)

    print("Training complete.")

    # --------------------------------------------------------
    # Validation evaluation
    # --------------------------------------------------------

    print("\nEvaluating validation set...")

    val_metrics = evaluate(
        model,
        X_val,
        y_val
    )

    print_metrics(
        "VALIDATION RESULTS",
        val_metrics
    )

    # --------------------------------------------------------
    # Test evaluation
    # --------------------------------------------------------

    print("\nEvaluating test set...")

    test_metrics = evaluate(
        model,
        X_test,
        y_test
    )

    print_metrics(
        "TEST RESULTS",
        test_metrics
    )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("BASELINE COMPLETE")
    print("=" * 60)

    print("\nThis Logistic Regression model is our")
    print("non-GNN baseline for comparison with GraphSAGE.")

    print("\nTest F1:")
    print(f"{test_metrics['f1']:.4f}")

    print("\nTest ROC-AUC:")
    print(f"{test_metrics['roc_auc']:.4f}")


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    main()