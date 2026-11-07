from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch_geometric.data import Data


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

EDGE_FEATURES = [
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


def load_graph_edges(filename):
    path = DATA_DIR / filename

    print(f"Loading: {path}")

    df = pd.read_csv(path)

    print(f"Rows: {len(df):,}")

    return df


def create_graph(df):
    """
    Convert one temporal graph window into a PyTorch Geometric Data object.
    """

    # ---------------------------------------------------------
    # Node count
    # ---------------------------------------------------------

    num_nodes = max(
        df["src_node"].max(),
        df["dst_node"].max()
    ) + 1

    num_nodes = int(num_nodes)

    # ---------------------------------------------------------
    # Edge index
    # ---------------------------------------------------------

    edge_index = torch.tensor(
        df[["src_node", "dst_node"]].values.T,
        dtype=torch.long
    )

    # ---------------------------------------------------------
    # Edge features
    # ---------------------------------------------------------

    edge_attr = torch.tensor(
        df[EDGE_FEATURES].values,
        dtype=torch.float32
    )

    # ---------------------------------------------------------
    # Edge labels
    # ---------------------------------------------------------

    y = torch.tensor(
        df["label"].values,
        dtype=torch.long
    )

    # ---------------------------------------------------------
    # Basic node features
    #
    # Each node gets:
    #   1. outgoing edge count
    #   2. incoming edge count
    #   3. outgoing flow count
    #   4. incoming flow count
    # ---------------------------------------------------------

    node_features = np.zeros((num_nodes, 4), dtype=np.float32)

    src_nodes = df["src_node"].to_numpy()
    dst_nodes = df["dst_node"].to_numpy()
    flow_counts = df["flow_count"].to_numpy(dtype=np.float32)

    for src, dst, flow_count in zip(
        src_nodes,
        dst_nodes,
        flow_counts
    ):
        node_features[src, 0] += 1
        node_features[dst, 1] += 1

        node_features[src, 2] += flow_count
        node_features[dst, 3] += flow_count

    x = torch.tensor(
        node_features,
        dtype=torch.float32
    )

    # ---------------------------------------------------------
    # Create PyG graph
    # ---------------------------------------------------------

    graph = Data(
        x=x,
        edge_index=edge_index,
        edge_attr=edge_attr,
        y=y,
        num_nodes=num_nodes
    )

    return graph


def build_temporal_graphs(filename):
    """
    Convert all temporal windows in a split into graph objects.
    """

    df = load_graph_edges(filename)

    graphs = []

    grouped = df.groupby("time_window")

    print(f"Time windows: {len(grouped):,}")

    for index, (time_window, window_df) in enumerate(grouped):

        graph = create_graph(window_df)

        graph.time_window = int(time_window)

        graphs.append(graph)

        if (index + 1) % 100 == 0:
            print(
                f"Processed {index + 1:,} / "
                f"{len(grouped):,} windows"
            )

    return graphs


def summarize_graphs(graphs, name):

    total_edges = sum(
        graph.edge_index.shape[1]
        for graph in graphs
    )

    total_nodes = sum(
        graph.num_nodes
        for graph in graphs
    )

    attack_edges = sum(
        int(graph.y.sum())
        for graph in graphs
    )

    normal_edges = total_edges - attack_edges

    print("\n" + "=" * 40)
    print(f"{name.upper()} GRAPH SUMMARY")
    print("=" * 40)

    print(f"Graphs/windows : {len(graphs):,}")
    print(f"Total nodes    : {total_nodes:,}")
    print(f"Total edges    : {total_edges:,}")
    print(f"Normal edges   : {normal_edges:,}")
    print(f"Attack edges   : {attack_edges:,}")

    if graphs:
        print("\nFirst graph:")
        print(graphs[0])


if __name__ == "__main__":

    train_graphs = build_temporal_graphs(
        "UNSW_NB15_graph_train.csv"
    )

    val_graphs = build_temporal_graphs(
        "UNSW_NB15_graph_val.csv"
    )

    test_graphs = build_temporal_graphs(
        "UNSW_NB15_graph_test.csv"
    )

    summarize_graphs(
        train_graphs,
        "Training"
    )

    summarize_graphs(
        val_graphs,
        "Validation"
    )

    summarize_graphs(
        test_graphs,
        "Test"
    )