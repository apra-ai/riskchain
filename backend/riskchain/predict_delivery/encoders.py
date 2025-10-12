# predict_delivery/encoders.py
from dataclasses import dataclass
from typing import Dict, List
from supplychains.data_structure import (
    CROSSES_BORDER, TRANSPORT_MODES_CHOICES, COST_CLASS, RELIABILITY_CLASS, DISTANCE_CLASS,
    NODE_ROLE_CHOICES, OWNERSHIP_CHOICES, CAPACITY_CLASS_CHOICES,  # falls Node-Encoder auch hier liegt
)

def _choice_keys(choices):
    return [k for k, _ in choices]

# ---------- Node ----------
@dataclass(frozen=True)
class NodeOneHotEncoder:
    node_role_index: Dict[str, int]
    ownership_index: Dict[str, int]
    capacity_class_index: Dict[str, int]

    @property
    def dim(self) -> int:
        return (len(self.node_role_index) +
                len(self.ownership_index) +
                len(self.capacity_class_index))

    def encode(self, node) -> List[int]:
        vec = [0] * self.dim
        off = 0
        i = self.node_role_index.get(node.node_role);        vec[off + i] = 1 if i is not None else 0
        off += len(self.node_role_index)
        i = self.ownership_index.get(node.ownership);        vec[off + i] = 1 if i is not None else 0
        off += len(self.ownership_index)
        i = self.capacity_class_index.get(node.capacity_class); vec[off + i] = 1 if i is not None else 0
        return vec

def build_node_encoder() -> NodeOneHotEncoder:
    return NodeOneHotEncoder(
        node_role_index={k: i for i, k in enumerate(_choice_keys(NODE_ROLE_CHOICES))},
        ownership_index={k: i for i, k in enumerate(_choice_keys(OWNERSHIP_CHOICES))},
        capacity_class_index={k: i for i, k in enumerate(_choice_keys(CAPACITY_CLASS_CHOICES))},
    )

# ---------- Edge ----------
@dataclass(frozen=True)
class EdgeOneHotEncoder:
    crosses_border_index: Dict[str, int]
    transport_modes_index: Dict[str, int]
    cost_index: Dict[str, int]
    reliability_index: Dict[str, int]
    distance_index: Dict[str, int]

    @property
    def dim(self) -> int:
        return (len(self.crosses_border_index) +
                len(self.transport_modes_index) +
                len(self.cost_index) +
                len(self.reliability_index) +
                len(self.distance_index))

    def encode(self, edge) -> List[int]:
        """One-Hot-Liste für: cross_border | transport_modes | cost | reliability | distance"""
        vec = [0] * self.dim
        off = 0

        i = self.crosses_border_index.get(edge.crosses_border)
        if i is not None: vec[off + i] = 1
        off += len(self.crosses_border_index)

        i = self.transport_modes_index.get(edge.transport_modes)
        if i is not None: vec[off + i] = 1
        off += len(self.transport_modes_index)

        i = self.cost_index.get(edge.cost)
        if i is not None: vec[off + i] = 1
        off += len(self.cost_index)

        i = self.reliability_index.get(edge.reliability)
        if i is not None: vec[off + i] = 1
        off += len(self.reliability_index)

        i = self.distance_index.get(edge.distance)
        if i is not None: vec[off + i] = 1

        return vec

def build_edge_encoder() -> EdgeOneHotEncoder:
    return EdgeOneHotEncoder(
        crosses_border_index={k: i for i, k in enumerate(_choice_keys(CROSSES_BORDER))},
        transport_modes_index={k: i for i, k in enumerate(_choice_keys(TRANSPORT_MODES_CHOICES))},
        cost_index={k: i for i, k in enumerate(_choice_keys(COST_CLASS))},
        reliability_index={k: i for i, k in enumerate(_choice_keys(RELIABILITY_CLASS))},
        distance_index={k: i for i, k in enumerate(_choice_keys(DISTANCE_CLASS))},
    )

def encode_supplychain_chain(supplychain, node_encoder: NodeOneHotEncoder, edge_encoder: EdgeOneHotEncoder) -> List[List[int]]:
    """Encodes each chain step of the supplychain into a list of one-hot vectors."""
    encoded_steps = []
    for chain in supplychain.steps_ordered():
        from_node_vec = chain.edge.from_node.onehot(node_encoder)
        to_node_vec = chain.edge.to_node.onehot(node_encoder)
        edge_vec = chain.edge.onehot(edge_encoder)
        chain_vec = from_node_vec + edge_vec + to_node_vec
        encoded_steps.append(chain_vec)
    return encoded_steps