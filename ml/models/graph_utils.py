from pathlib import Path

import numpy as np
import torch
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def fit_edge_scaler(graphs):
    """
    Fit StandardScaler using TRAINING graphs only.
    """

    edge_features = []

    for graph in graphs:
        edge_features.append(
            graph.edge_attr.numpy()
        )

    edge_features = np.vstack(edge_features)

    scaler = StandardScaler()

    scaler.fit(edge_features)

    return scaler


def transform_graphs(graphs, scaler):
    """
    Apply a previously fitted scaler to graph edge features.
    """

    transformed_graphs = []

    for graph in graphs:

        edge_attr = scaler.transform(
            graph.edge_attr.numpy()
        )

        graph.edge_attr = torch.tensor(
            edge_attr,
            dtype=torch.float32
        )

        transformed_graphs.append(graph)

    return transformed_graphs 