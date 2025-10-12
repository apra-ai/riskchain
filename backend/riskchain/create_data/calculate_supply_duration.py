from supplychains.models import Node, Edge
import random

# Node-bezogene choices
NODE_ROLE_CHOICES_VALUES = {
    "SUPPLIER": 2,
    "MANUFACTURER": 3,
    "PLANT": 1,
    "WAREHOUSE": 2,
    "DISTRIBUTION_CENTER": 1,
    "PORT": 2,
    "AIRPORT": 1,
    "CROSSDOCK": 4,
    "CUSTOMER": 6,
}

OWNERSHIP_CHOICES_VALUES = {
    "INTERNAL": 1,
    "3PL": 4,
    "SUPPLIER_OWNED": 2,
    "JV": 2,
    "GOVERNMENT": 7,
}

CAPACITY_CLASS_CHOICES_VALUES = {
    "LOW": 1,
    "MEDIUM": 3,
    "HIGH": 6,
}

# Edge-bezogene choices
CROSSES_BORDER_VALUES = {
    "YES": 5,
    "NO": 1,
}

COST_CLASS_VALUES = {
    "LOW": 3,
    "MEDIUM": 1,
    "HIGH": 2,
}

RELIABILITY_CLASS_VALUES = {
    "LOW": 5,
    "MEDIUM": 3,
    "HIGH": 1,
}

DISTANCE_CLASS_VALUES = {
    "SHORT": 1,
    "MEDIUM": 3,
    "LONG": 5,
}

TRANSPORT_MODES_CHOICES_VALUES = {
    "ROAD": 5,
    "RAIL": 3,
    "AIR": 1,
    "SEA": 8,
    "INLAND_WATERWAY": 6,
}

for node in Node.objects.all():
    delay_score = 1
    sigma = 0.5 # Standardabweichung für die Gaußsche Verteilung
    delay_score *= max(1, random.gauss(NODE_ROLE_CHOICES_VALUES.get(node.node_role, 1),sigma))
    delay_score += max(1, random.gauss(OWNERSHIP_CHOICES_VALUES.get(node.ownership, 1),sigma))
    delay_score *= max(1, random.gauss(CAPACITY_CLASS_CHOICES_VALUES.get(node.capacity_class, 1),sigma))
    node.delay_score = delay_score
    node.save()

for edge in Edge.objects.all():
    delay_score = 1
    sigma = 0.5 # Standardabweichung für die Gaußsche Verteilung
    delay_score *= max(1, random.gauss(CROSSES_BORDER_VALUES.get(edge.crosses_border, 1),sigma))
    delay_score *= max(1, random.gauss(COST_CLASS_VALUES.get(edge.cost, 1),sigma))
    delay_score *= max(1, random.gauss(RELIABILITY_CLASS_VALUES.get(edge.reliability, 1),sigma))
    delay_score *= max(1, random.gauss(DISTANCE_CLASS_VALUES.get(edge.distance, 1),sigma))
    delay_score *= max(1, random.gauss(TRANSPORT_MODES_CHOICES_VALUES.get(edge.transport_modes, 1),sigma))
    delay_score += edge.from_node.delay_score
    delay_score += edge.to_node.delay_score
    edge.delay_score = delay_score
    edge.save()