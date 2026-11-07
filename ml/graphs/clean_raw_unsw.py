import pandas as pd
import numpy as np
import os

RAW_DATA_PATH = "data/UNSW_NB15_raw_combined.csv"
OUTPUT_PATH = "data/UNSW_NB15_graph_ready.csv"


# Columns that should contain numeric values
NUMERIC_COLUMNS = [
    "sport",
    "dsport",
    "dur",
    "sbytes",
    "dbytes",
    "sttl",
    "dttl",
    "sloss",
    "dloss",
    "Sload",
    "Dload",
    "Spkts",
    "Dpkts",
    "swin",
    "dwin",
    "stcpb",
    "dtcpb",
    "smeansz",
    "dmeansz",
    "trans_depth",
    "res_bdy_len",
    "Sjit",
    "Djit",
    "Stime",
    "Ltime",
    "Sintpkt",
    "Dintpkt",
    "tcprtt",
    "synack",
    "ackdat",
    "is_sm_ips_ports",
    "ct_state_ttl",
    "ct_flw_http_mthd",
    "is_ftp_login",
    "ct_ftp_cmd",
    "ct_srv_src",
    "ct_srv_dst",
    "ct_dst_ltm",
    "ct_src_ltm",
    "ct_src_dport_ltm",
    "ct_dst_sport_ltm",
    "ct_dst_src_ltm",
    "label",
]


def clean_raw_data(df):
    """Clean raw UNSW-NB15 data for graph construction."""

    print("\n========================================")
    print("STARTING RAW DATA CLEANING")
    print("========================================")

    # --------------------------------------------------
    # 1. Remove whitespace from string columns
    # --------------------------------------------------
    print("\n[1] Cleaning string columns...")

    string_columns = [
        "srcip",
        "dstip",
        "proto",
        "state",
        "service",
        "attack_cat",
    ]

    for column in string_columns:
        df[column] = df[column].astype("string").str.strip()

    # --------------------------------------------------
    # 2. Clean IP addresses
    # --------------------------------------------------
    print("[2] Cleaning IP addresses...")

    df["srcip"] = df["srcip"].replace(
        ["", "nan", "None", "<NA>"],
        pd.NA
    )

    df["dstip"] = df["dstip"].replace(
        ["", "nan", "None", "<NA>"],
        pd.NA
    )

    # --------------------------------------------------
    # 3. Convert numeric columns
    # --------------------------------------------------
    print("[3] Converting numeric columns...")

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # --------------------------------------------------
    # 4. Clean attack category
    # --------------------------------------------------
    print("[4] Cleaning attack categories...")

    df["attack_cat"] = (
        df["attack_cat"]
        .fillna("Normal")
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------
    # 5. Remove invalid communication records
    # --------------------------------------------------
    print("[5] Removing invalid communication records...")

    before = len(df)

    df = df.dropna(
        subset=["srcip", "dstip", "label"]
    )

    after = len(df)

    print("Removed rows:", before - after)

    # --------------------------------------------------
    # 6. Remove duplicate communication records
    # --------------------------------------------------
    print("[6] Checking duplicate rows...")

    duplicates = df.duplicated().sum()

    print("Duplicate rows:", duplicates)

    if duplicates > 0:
        df = df.drop_duplicates()

    # --------------------------------------------------
    # 7. Make label integer
    # --------------------------------------------------
    df["label"] = df["label"].astype(int)

    # --------------------------------------------------
    # 8. Sort by start time
    # --------------------------------------------------
    print("[7] Sorting records by time...")

    if "Stime" in df.columns:
        df = df.sort_values(
            by="Stime",
            kind="stable"
        )

    # --------------------------------------------------
    # 9. Reset index
    # --------------------------------------------------
    df = df.reset_index(drop=True)

    return df


def print_cleaning_summary(df):
    """Print final dataset information."""

    print("\n========================================")
    print("CLEANING SUMMARY")
    print("========================================")

    print("\nDataset shape:")
    print(df.shape)

    print("\nMissing values:")
    print(df.isnull().sum().sum())

    print("\nLabel distribution:")
    print(df["label"].value_counts())

    print("\nAttack categories:")
    print(df["attack_cat"].value_counts(dropna=False))

    print("\nUnique source hosts:")
    print(df["srcip"].nunique())

    print("\nUnique destination hosts:")
    print(df["dstip"].nunique())

    print("\nProtocols:")
    print(df["proto"].value_counts().head(10))

    print("\nServices:")
    print(df["service"].value_counts().head(10))


if __name__ == "__main__":

    print("========================================")
    print("UNSW-NB15 GRAPH DATA CLEANER")
    print("========================================")

    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(
            f"Raw combined dataset not found: {RAW_DATA_PATH}"
        )

    print("\nLoading raw combined dataset...")

    df = pd.read_csv(
        RAW_DATA_PATH,
        low_memory=False
    )

    print("Original shape:", df.shape)

    df = clean_raw_data(df)

    print_cleaning_summary(df)

    print("\nSaving graph-ready dataset...")

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\nSaved to:")
    print(OUTPUT_PATH)

    print("\n========================================")
    print("CLEANING COMPLETE")
    print("========================================")