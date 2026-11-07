import pandas as pd
import os

EDGES_PATH = "data/UNSW_NB15_graph_edges.csv"
NODES_PATH = "data/UNSW_NB15_nodes.csv"


if __name__ == "__main__":

    print("========================================")
    print("DYNAMIC GRAPH INSPECTION")
    print("========================================")

    # -----------------------------------------
    # Load nodes
    # -----------------------------------------

    print("\nLoading node mapping...")

    nodes = pd.read_csv(NODES_PATH)

    print("Number of nodes:", len(nodes))

    print("\n===== NODE MAPPING =====")
    print(nodes.to_string(index=False))

    # -----------------------------------------
    # Load edges
    # -----------------------------------------

    print("\nLoading graph edges...")

    edges = pd.read_csv(
        EDGES_PATH,
        low_memory=False
    )

    print("Number of edges:", len(edges))

    # -----------------------------------------
    # Basic information
    # -----------------------------------------

    print("\n===== EDGE COLUMNS =====")

    print(edges.columns.tolist())

    # -----------------------------------------
    # Time windows
    # -----------------------------------------

    print("\n===== TIME WINDOWS =====")

    print(
        "Number of time windows:",
        edges["time_window"].nunique()
    )

    print(
        "First time window:",
        edges["time_window"].min()
    )

    print(
        "Last time window:",
        edges["time_window"].max()
    )

    # -----------------------------------------
    # Edge label distribution
    # -----------------------------------------

    print("\n===== EDGE LABEL DISTRIBUTION =====")

    print(
        edges["label"].value_counts()
    )

    # -----------------------------------------
    # Attack ratio
    # -----------------------------------------

    print("\n===== ATTACK RATIO =====")

    print(
        edges["attack_ratio"].describe()
    )

    # -----------------------------------------
    # Sample normal edges
    # -----------------------------------------

    print("\n===== SAMPLE NORMAL EDGES =====")

    normal_edges = edges[
        edges["label"] == 0
    ]

    print(
        normal_edges[
            [
                "time_window",
                "srcip",
                "dstip",
                "src_node",
                "dst_node",
                "flow_count",
                "attack_count",
                "attack_ratio",
                "label"
            ]
        ].head(10)
    )

    # -----------------------------------------
    # Sample attack edges
    # -----------------------------------------

    print("\n===== SAMPLE ATTACK EDGES =====")

    attack_edges = edges[
        edges["label"] == 1
    ]

    print(
        attack_edges[
            [
                "time_window",
                "srcip",
                "dstip",
                "src_node",
                "dst_node",
                "flow_count",
                "attack_count",
                "attack_ratio",
                "label"
            ]
        ].head(10)
    )

    # -----------------------------------------
    # Most active communication pairs
    # -----------------------------------------

    print("\n===== MOST ACTIVE COMMUNICATION PAIRS =====")

    pairs = (
        edges
        .groupby(
            ["srcip", "dstip"]
        )
        .size()
        .sort_values(
            ascending=False
        )
        .head(10)
    )

    print(pairs)

    # -----------------------------------------
    # Most active source nodes
    # -----------------------------------------

    print("\n===== MOST ACTIVE SOURCE NODES =====")

    source_activity = (
        edges
        .groupby("src_node")
        ["flow_count"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
    )

    print(source_activity)

    # -----------------------------------------
    # Final validation
    # -----------------------------------------

    print("\n========================================")
    print("GRAPH VALIDATION COMPLETE")
    print("========================================")