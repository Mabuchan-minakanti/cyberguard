import pandas as pd
import numpy as np
import os


INPUT_PATH = "data/UNSW_NB15_graph_ready.csv"
OUTPUT_PATH = "data/UNSW_NB15_graph_edges.csv"

# Number of seconds represented by one graph snapshot
WINDOW_SECONDS = 60


# Features that will be aggregated for each
# source → destination communication pair.
EDGE_FEATURES = [
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


def load_graph_ready_data():
    print("\nLoading graph-ready dataset...")

    df = pd.read_csv(
        INPUT_PATH,
        low_memory=False
    )

    print("Shape:", df.shape)

    return df


def prepare_timestamps(df):
    """
    Convert UNSW-NB15 start time into
    graph time-window IDs.
    """

    print("\nPreparing timestamps...")

    df["Stime"] = pd.to_numeric(
        df["Stime"],
        errors="coerce"
    )

    # Remove records without a valid timestamp
    df = df.dropna(
        subset=["Stime"]
    ).copy()

    # Start time of the complete dataset
    min_time = df["Stime"].min()

    # Convert absolute timestamp into
    # a relative time window.
    df["time_window"] = (
        (df["Stime"] - min_time)
        // WINDOW_SECONDS
    ).astype(int)

    print("Minimum timestamp:", min_time)
    print("Maximum timestamp:", df["Stime"].max())
    print("Number of time windows:", df["time_window"].nunique())

    return df


def build_edge_features(df):
    """
    Aggregate flow records into directed
    source → destination communication edges.
    """

    print("\nBuilding communication edges...")

    group_columns = [
        "time_window",
        "srcip",
        "dstip",
    ]

    # Count how many flows occurred between
    # each source/destination pair.
    grouped = (
    df.groupby(group_columns)
    .agg(
        flow_count=("label", "size"),
        label=("label", "max"),
        **{
            feature: (feature, "mean")
            for feature in EDGE_FEATURES
        }
    )
    .reset_index()
)

    return grouped


def create_node_mapping(df):
    """
    Create a unique integer ID for every host.
    """

    print("\nCreating node mapping...")

    hosts = pd.concat(
        [
            df["srcip"],
            df["dstip"]
        ]
    ).dropna().unique()

    hosts = sorted(hosts)

    node_mapping = pd.DataFrame(
        {
            "node_id": range(len(hosts)),
            "ip": hosts
        }
    )

    return node_mapping


def add_node_ids(edges, node_mapping):
    """
    Convert IP addresses into integer node IDs.
    """

    print("\nAdding node IDs...")

    ip_to_id = dict(
        zip(
            node_mapping["ip"],
            node_mapping["node_id"]
        )
    )

    edges["src_node"] = edges["srcip"].map(
        ip_to_id
    )

    edges["dst_node"] = edges["dstip"].map(
        ip_to_id
    )

    return edges


def save_outputs(edges, node_mapping):

    os.makedirs(
        "data",
        exist_ok=True
    )

    print("\nSaving graph edges...")

    edges.to_csv(
        OUTPUT_PATH,
        index=False
    )

    node_path = "data/UNSW_NB15_nodes.csv"

    node_mapping.to_csv(
        node_path,
        index=False
    )

    print("Edges saved to:")
    print(OUTPUT_PATH)

    print("\nNodes saved to:")
    print(node_path)


def print_summary(edges, node_mapping):

    print("\n========================================")
    print("DYNAMIC GRAPH SUMMARY")
    print("========================================")

    print("\nNumber of nodes:")
    print(len(node_mapping))

    print("\nNumber of graph edges:")
    print(len(edges))

    print("\nNumber of time windows:")
    print(
        edges["time_window"].nunique()
    )

    print("\nAttack edges:")
    print(
        (edges["label"] == 1).sum()
    )

    print("\nNormal edges:")
    print(
        (edges["label"] == 0).sum()
    )

    print("\nSample edges:")

    print(
        edges[
          [
             "time_window",
             "src_node",
             "dst_node",
             "flow_count",
             "label"
          ]
        ].head(20)
    )


if __name__ == "__main__":

    print("========================================")
    print("UNSW-NB15 DYNAMIC GRAPH BUILDER")
    print("========================================")

    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_PATH}"
        )

    df = load_graph_ready_data()

    df = prepare_timestamps(df)

    node_mapping = create_node_mapping(df)

    edges = build_edge_features(df)

    edges = add_node_ids(
        edges,
        node_mapping
    )

    print_summary(
        edges,
        node_mapping
    )

    save_outputs(
        edges,
        node_mapping
    )

    print("\n========================================")
    print("GRAPH CONSTRUCTION COMPLETE")
    print("========================================")