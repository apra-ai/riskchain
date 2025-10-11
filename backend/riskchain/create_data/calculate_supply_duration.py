from supplychains.models import Node, Edge
import random

# Node-bezogene choices
NODE_ROLE_CHOICES_VALUES = {
    "SUPPLIER": 1,
    "MANUFACTURER": 1,
    "PLANT": 1,
    "WAREHOUSE": 1,
    "DISTRIBUTION_CENTER": 1,
    "PORT": 1,
    "AIRPORT": 1,
    "CROSSDOCK": 1,
    "CUSTOMER": 1,
}

OWNERSHIP_CHOICES_VALUES = {
    "INTERNAL": 1,
    "3PL": 1,
    "SUPPLIER_OWNED": 1,
    "JV": 1,
    "GOVERNMENT": 1,
}

CAPACITY_CLASS_CHOICES_VALUES = {
    "LOW": 1,
    "MEDIUM": 1,
    "HIGH": 1,
}

# Edge-bezogene choices
CROSSES_BORDER_VALUES = {
    "YES": 1,
    "NO": 1,
}

COST_CLASS_VALUES = {
    "LOW": 1,
    "MEDIUM": 1,
    "HIGH": 1,
}

RELIABILITY_CLASS_VALUES = {
    "LOW": 1,
    "MEDIUM": 1,
    "HIGH": 1,
}

DISTANCE_CLASS_VALUES = {
    "SHORT": 1,
    "MEDIUM": 1,
    "LONG": 1,
}

TRANSPORT_MODES_CHOICES_VALUES = {
    "ROAD": 1,
    "RAIL": 1,
    "AIR": 1,
    "SEA": 1,
    "INLAND_WATERWAY": 1,
}

for node in Node.objects.all():
    delay_score = 1
    sigma = 0.5 # Standardabweichung für die Gaußsche Verteilung
    delay_score *= max(1, random.gauss(NODE_ROLE_CHOICES_VALUES.get(node.node_role, 1),sigma))
    delay_score += max(1, random.gauss(OWNERSHIP_CHOICES_VALUES.get(node.ownership, 1),sigma))
    delay_score *= max(1, random.gauss(CAPACITY_CLASS_CHOICES_VALUES.get(node.capacity_class, 1),10))
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