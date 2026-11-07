import torch
import torch.nn as nn
import torch.nn.functional as F

from torch_geometric.nn import SAGEConv


class GraphSAGEEdgeClassifier(nn.Module):

    def __init__(
        self,
        node_features=4,
        edge_features=15,
        hidden_channels=64,
        dropout=0.2
    ):
        super().__init__()

        self.dropout = dropout

        # ---------------------------------------------
        # GraphSAGE layers
        # ---------------------------------------------

        self.conv1 = SAGEConv(
            node_features,
            hidden_channels
        )

        self.conv2 = SAGEConv(
            hidden_channels,
            hidden_channels
        )

        # ---------------------------------------------
        # Edge classifier
        #
        # source embedding
        # destination embedding
        # edge traffic features
        # ---------------------------------------------

        classifier_input = (
            hidden_channels
            + hidden_channels
            + edge_features
        )

        self.edge_classifier = nn.Sequential(
            nn.Linear(
                classifier_input,
                64
            ),

            nn.ReLU(),

            nn.Dropout(dropout),

            nn.Linear(
                64,
                32
            ),

            nn.ReLU(),

            nn.Dropout(dropout),

            nn.Linear(
                32,
                1
            )
        )

    def encode_nodes(
        self,
        x,
        edge_index
    ):

        x = self.conv1(
            x,
            edge_index
        )

        x = F.relu(x)

        x = F.dropout(
            x,
            p=self.dropout,
            training=self.training
        )

        x = self.conv2(
            x,
            edge_index
        )

        x = F.relu(x)

        return x

    def classify_edges(
        self,
        node_embeddings,
        edge_index,
        edge_attr
    ):

        src = edge_index[0]
        dst = edge_index[1]

        src_embedding = node_embeddings[src]
        dst_embedding = node_embeddings[dst]

        edge_input = torch.cat(
            [
                src_embedding,
                dst_embedding,
                edge_attr
            ],
            dim=1
        )

        logits = self.edge_classifier(
            edge_input
        ).squeeze(-1)

        return logits

    def forward(
        self,
        x,
        edge_index,
        edge_attr
    ):

        node_embeddings = self.encode_nodes(
            x,
            edge_index
        )

        logits = self.classify_edges(
            node_embeddings,
            edge_index,
            edge_attr
        )

        return logits