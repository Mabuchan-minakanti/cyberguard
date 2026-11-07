import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# =========================
# Paths
# =========================

TRAIN_PATH = "data/UNSW_NB15_training-set.csv"
TEST_PATH = "data/UNSW_NB15_testing-set.csv"

TRAIN_OUTPUT_PATH = "data/UNSW_NB15_training_processed.csv"
TEST_OUTPUT_PATH = "data/UNSW_NB15_testing_processed.csv"

PREPROCESSOR_PATH = "data/unsw_nb15_preprocessor.joblib"


# =========================
# Load dataset
# =========================

def load_dataset(path):
    """Load a dataset from CSV."""
    return pd.read_csv(path)


# =========================
# Separate features/targets
# =========================

def separate_features(df):
    """
    Separate model inputs from target information.
    """

    y = df["label"].copy()
    attack_categories = df["attack_cat"].copy()

    # Remove identifier and target columns
    X = df.drop(
        columns=["id", "label", "attack_cat"]
    )

    return X, y, attack_categories


# =========================
# Create preprocessor
# =========================

def create_preprocessor(X):
    """Create the numerical + categorical preprocessing pipeline."""

    categorical_columns = [
        "proto",
        "service",
        "state"
    ]

    numerical_columns = [
        column
        for column in X.columns
        if column not in categorical_columns
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numerical",
                StandardScaler(),
                numerical_columns
            ),
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False
                ),
                categorical_columns
            )
        ]
    )

    return preprocessor


# =========================
# Process dataset
# =========================

def process_dataset(
    X,
    y,
    attack_categories,
    preprocessor,
    fit=False
):
    """Fit or apply the preprocessing pipeline."""

    if fit:
        X_processed = preprocessor.fit_transform(X)
    else:
        X_processed = preprocessor.transform(X)

    feature_names = preprocessor.get_feature_names_out()

    X_processed = pd.DataFrame(
        X_processed,
        columns=feature_names
    )

    return X_processed, y, attack_categories


# =========================
# Main
# =========================

if __name__ == "__main__":

    print("========================================")
    print("UNSW-NB15 PREPROCESSING")
    print("========================================")

    # ------------------------------------
    # Load training data
    # ------------------------------------

    print("\nLoading training dataset...")

    train_df = load_dataset(TRAIN_PATH)

    print("Training shape:", train_df.shape)

    # ------------------------------------
    # Load testing data
    # ------------------------------------

    print("\nLoading testing dataset...")

    test_df = load_dataset(TEST_PATH)

    print("Testing shape:", test_df.shape)

    # ------------------------------------
    # Separate features and targets
    # ------------------------------------

    X_train, y_train, attack_train = separate_features(
        train_df
    )

    X_test, y_test, attack_test = separate_features(
        test_df
    )

    print("\nTraining features:", X_train.shape)
    print("Testing features:", X_test.shape)

    # ------------------------------------
    # Create preprocessing pipeline
    # ------------------------------------

    preprocessor = create_preprocessor(X_train)

    # ------------------------------------
    # FIT ONLY ON TRAINING DATA
    # ------------------------------------

    print("\nFitting preprocessor on training data...")

    X_train_processed, y_train, attack_train = process_dataset(
        X_train,
        y_train,
        attack_train,
        preprocessor,
        fit=True
    )

    # ------------------------------------
    # TRANSFORM TEST DATA
    # ------------------------------------

    print("Transforming testing data...")

    X_test_processed, y_test, attack_test = process_dataset(
        X_test,
        y_test,
        attack_test,
        preprocessor,
        fit=False
    )

    # ------------------------------------
    # Save processed datasets
    # ------------------------------------

    X_train_processed.to_csv(
        TRAIN_OUTPUT_PATH,
        index=False
    )

    X_test_processed.to_csv(
        TEST_OUTPUT_PATH,
        index=False
    )

    # ------------------------------------
    # Save fitted preprocessor
    # ------------------------------------

    joblib.dump(
        preprocessor,
        PREPROCESSOR_PATH
    )

    # ------------------------------------
    # Results
    # ------------------------------------

    print("\n========================================")
    print("PREPROCESSING COMPLETE")
    print("========================================")

    print("\nTraining processed shape:")
    print(X_train_processed.shape)

    print("\nTesting processed shape:")
    print(X_test_processed.shape)

    print("\nTraining labels:")
    print(y_train.value_counts())

    print("\nTesting labels:")
    print(y_test.value_counts())

    print("\nSaved files:")
    print(TRAIN_OUTPUT_PATH)
    print(TEST_OUTPUT_PATH)
    print(PREPROCESSOR_PATH)