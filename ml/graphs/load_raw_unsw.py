import pandas as pd
import glob


DATA_PATTERN = "data/UNSW-NB15_*.csv"


COLUMN_NAMES = [
    "srcip",
    "sport",
    "dstip",
    "dsport",
    "proto",
    "state",
    "dur", 
    "sbytes",
    "dbytes",
    "sttl",
    "dttl",
    "sloss",
    "dloss",
    "service",
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
    "attack_cat",
    "label",
]


def load_raw_unsw():
    """Load all original UNSW-NB15 CSV files."""

    files = sorted(glob.glob(DATA_PATTERN))

    if not files:
        raise FileNotFoundError(
            "No UNSW-NB15 original CSV files found."
        )

    print("Files found:")

    for file in files:
        print(f"  - {file}")

    dataframes = []

    for file in files:
        print(f"\nLoading {file}...")

        df = pd.read_csv(
            file,
            header=None,
            names=COLUMN_NAMES,
            encoding="utf-8-sig",
            low_memory=False
        )

        dataframes.append(df)

        print("Shape:", df.shape)

    combined_df = pd.concat(
        dataframes,
        ignore_index=True
    )

    return combined_df


if __name__ == "__main__":

    print("========================================")
    print("UNSW-NB15 RAW DATA LOADER")
    print("========================================")

    df = load_raw_unsw()
    output_path = "data/UNSW_NB15_raw_combined.csv"

    print("\nSaving combined raw dataset...")
    df.to_csv(output_path, index=False)

    print("Saved to:", output_path)
    print("\n===== COMBINED DATASET =====")
    print("Shape:", df.shape)

    print("\n===== COLUMNS =====")
    print(df.columns.tolist())

    print("\n===== SOURCE / DESTINATION SAMPLE =====")
    print(
        df[
            [
                "srcip",
                "sport",
                "dstip",
                "dsport",
                "proto",
                "label",
            ]
        ].head()
    )

    print("\n===== LABEL DISTRIBUTION =====")
    print(df["label"].value_counts(dropna=False))

    print("\n===== UNIQUE HOSTS =====")
    print("Source IPs:", df["srcip"].nunique())
    print("Destination IPs:", df["dstip"].nunique())