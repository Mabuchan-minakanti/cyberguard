import pandas as pd

DATA_PATH = "data/UNSW_NB15_graph_ready.csv"


if __name__ == "__main__":

    print("========================================")
    print("GRAPH-READY DATA INSPECTION")
    print("========================================")

    df = pd.read_csv(
        DATA_PATH,
        low_memory=False
    )

    print("\n===== SHAPE =====")
    print(df.shape)

    print("\n===== MISSING VALUES BY COLUMN =====")

    missing = df.isnull().sum()

    missing = missing[missing > 0].sort_values(
        ascending=False
    )

    print(missing)

    print("\n===== MISSING VALUE PERCENTAGE =====")

    missing_percent = (
        df.isnull().mean() * 100
    )

    missing_percent = missing_percent[
        missing_percent > 0
    ].sort_values(
        ascending=False
    )

    print(missing_percent)

    print("\n===== SOURCE → DESTINATION SAMPLE =====")

    print(
        df[
            [
                "srcip",
                "sport",
                "dstip",
                "dsport",
                "proto",
                "service",
                "label",
                "attack_cat"
            ]
        ].head(10)
    )

    print("\n===== UNIQUE SOURCE → DESTINATION PAIRS =====")

    print(
        df[
            ["srcip", "dstip"]
        ].drop_duplicates().shape[0]
    )

    print("\n===== TOP COMMUNICATION PAIRS =====")

    pairs = (
        df.groupby(
            ["srcip", "dstip"]
        )
        .size()
        .sort_values(
            ascending=False
        )
        .head(20)
    )

    print(pairs)

    print("\n========================================")
    print("INSPECTION COMPLETE")
    print("========================================")