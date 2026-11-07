from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = PROJECT_ROOT / "data" / "UNSW_NB15_graph_edges.csv"

TRAIN_FILE = PROJECT_ROOT / "data" / "UNSW_NB15_graph_train.csv"
VAL_FILE = PROJECT_ROOT / "data" / "UNSW_NB15_graph_val.csv"
TEST_FILE = PROJECT_ROOT / "data" / "UNSW_NB15_graph_test.csv"


TRAIN_RATIO = 0.70
VAL_RATIO = 0.15


def main():
    print("=" * 40)
    print("UNSW-NB15 TEMPORAL GRAPH SPLIT")
    print("=" * 40)

    print("\nLoading graph edges...")
    df = pd.read_csv(INPUT_FILE)

    print(f"Total edges: {len(df):,}")

    # Sort by temporal window
    df = df.sort_values("time_window").reset_index(drop=True)

    # Get unique active time windows
    windows = sorted(df["time_window"].unique())

    total_windows = len(windows)

    train_end = int(total_windows * TRAIN_RATIO)
    val_end = int(total_windows * (TRAIN_RATIO + VAL_RATIO))

    train_windows = windows[:train_end]
    val_windows = windows[train_end:val_end]
    test_windows = windows[val_end:]

    train_df = df[df["time_window"].isin(train_windows)].copy()
    val_df = df[df["time_window"].isin(val_windows)].copy()
    test_df = df[df["time_window"].isin(test_windows)].copy()

    print("\nTemporal split:")
    print(f"Train windows: {len(train_windows):,}")
    print(f"Validation windows: {len(val_windows):,}")
    print(f"Test windows: {len(test_windows):,}")

    print("\nEdge counts:")
    print(f"Train edges: {len(train_df):,}")
    print(f"Validation edges: {len(val_df):,}")
    print(f"Test edges: {len(test_df):,}")

    print("\nLabel distribution:")

    print("\nTRAIN")
    print(train_df["label"].value_counts().sort_index())

    print("\nVALIDATION")
    print(val_df["label"].value_counts().sort_index())

    print("\nTEST")
    print(test_df["label"].value_counts().sort_index())

    print("\nTime ranges:")
    print(
        f"Train: {train_df['time_window'].min()} "
        f"-> {train_df['time_window'].max()}"
    )

    print(
        f"Validation: {val_df['time_window'].min()} "
        f"-> {val_df['time_window'].max()}"
    )

    print(
        f"Test: {test_df['time_window'].min()} "
        f"-> {test_df['time_window'].max()}"
    )

    # Save
    train_df.to_csv(TRAIN_FILE, index=False)
    val_df.to_csv(VAL_FILE, index=False)
    test_df.to_csv(TEST_FILE, index=False)

    print("\nSaved:")
    print(TRAIN_FILE)
    print(VAL_FILE)
    print(TEST_FILE)

    print("\n" + "=" * 40)
    print("TEMPORAL SPLIT COMPLETE")
    print("=" * 40)


if __name__ == "__main__":
    main()