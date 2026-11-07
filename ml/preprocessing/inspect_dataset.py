import pandas as pd


DATASET_PATH = "data/UNSW_NB15_training-set.csv"


def load_dataset():
    """Load the UNSW-NB15 training dataset."""
    df = pd.read_csv(DATASET_PATH)
    return df


def inspect_dataset(df):
    """Print basic information about the dataset."""

    print("\n===== DATASET SHAPE =====")
    print(df.shape)

    print("\n===== COLUMN NAMES =====")
    print(df.columns.tolist())

    print("\n===== DATA TYPES =====")
    print(df.dtypes)

    print("\n===== MISSING VALUES =====")
    print(df.isnull().sum())

    print("\n===== DUPLICATE ROWS =====")
    print(df.duplicated().sum())

    print("\n===== LABEL DISTRIBUTION =====")
    print(df["label"].value_counts())

    print("\n===== ATTACK CATEGORY DISTRIBUTION =====")
    print(df["attack_cat"].value_counts(dropna=False))


if __name__ == "__main__":
    dataset = load_dataset()
    inspect_dataset(dataset)