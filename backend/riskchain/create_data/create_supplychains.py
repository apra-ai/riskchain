# create_data/create_supplychains.py

from supplychains.data_structure import (
    CROSSES_BORDER, COST_CLASS, RELIABILITY_CLASS, DISTANCE_CLASS, TRANSPORT_MODES_CHOICES
)
from supplychains.models import Node, Edge, SupplyChain, ChainStep
from django.db import transaction
import random

# ---- Helper: Choice-Werte extrahieren (value,label) -> value -----------------
def _values_from_choices(choices):
    # choices kann Liste/Tuple von 2ern oder Enums sein; wir nehmen das erste Element
    return [c[0] if isinstance(c, (list, tuple)) else c for c in choices]

CROSSES_BORDER_VALUES = _values_from_choices(CROSSES_BORDER)
TRANSPORT_MODE_VALUES = _values_from_choices(TRANSPORT_MODES_CHOICES)
COST_VALUES = _values_from_choices(COST_CLASS)
RELIABILITY_VALUES = _values_from_choices(RELIABILITY_CLASS)
DISTANCE_VALUES = _values_from_choices(DISTANCE_CLASS)


def generate_supplychains(
    count: int = 10,
    min_len: int = 3,
    max_len: int = 10,
    seed: int | None = 42,
) -> int:
    """
    Erzeugt `count` Supply Chains mit linear verbundenen zufälligen Nodes.
    Pro Chain werden zwischen `min_len` und `max_len` Nodes gezogen.
    Gibt die Anzahl tatsächlich erzeugter Supply Chains zurück.
    """

    if seed is not None:
        random.seed(seed)

    # Alle Nodes einmal laden (wir brauchen city für die Beschreibung -> Instanzen laden)
    nodes = list(Node.objects.all())
    n_nodes = len(nodes)
    if n_nodes < 2:
        raise ValueError("Es werden mindestens 2 Nodes benötigt.")

    if min_len < 2:
        raise ValueError("min_len muss >= 2 sein (mind. Start- und Endknoten).")
    if max_len < min_len:
        raise ValueError("max_len muss >= min_len sein.")

    created_sc = 0

    # Eine Transaktion für den ganzen Batch (am schnellsten & konsistent)
    with transaction.atomic():
        for i in range(count):
            # Anzahl Nodes für diese Chain
            number_of_nodes_in_chain = random.randint(min_len, min(max_len, n_nodes))

            # Zufällige, eindeutige Node-Auswahl; random.sample gibt bereits eine zufällige Reihenfolge zurück
            selected_nodes = random.sample(nodes, number_of_nodes_in_chain)

            # Supply Chain anlegen
            origin_city = getattr(selected_nodes[0], "city", str(selected_nodes[0].pk))
            dest_city = getattr(selected_nodes[-1], "city", str(selected_nodes[-1].pk))

            supply_chain = SupplyChain.objects.create(
                name=f"Supply Chain {i+1}",
                description=f"From {origin_city} to {dest_city}",
                supply_duration_days=1
            )

            # Kanten + Steps erzeugen (linear verbinden)
            # Hinweis: get_or_create nur auf (from_node, to_node); weitere Felder via defaults NUR bei Neuerstellung
            steps_to_create = []
            for j in range(len(selected_nodes) - 1):
                from_node = selected_nodes[j]
                to_node = selected_nodes[j + 1]

                edge, _created = Edge.objects.get_or_create(
                    from_node=from_node,
                    to_node=to_node,
                    defaults={
                        "crosses_border": random.choice(CROSSES_BORDER_VALUES),
                        "transport_modes": random.choice(TRANSPORT_MODE_VALUES),
                        "cost": random.choice(COST_VALUES),
                        "reliability": random.choice(RELIABILITY_VALUES),
                        "distance": random.choice(DISTANCE_VALUES),
                    },
                )

                steps_to_create.append(
                    ChainStep(
                        chain=supply_chain,
                        position=j + 1,
                        edge=edge,
                    )
                )

            # Bulk für Steps (schneller als einzelne INSERTs)
            ChainStep.objects.bulk_create(steps_to_create)
            created_sc += 1

    return created_sc


# Optional: direkter Aufruf, falls Datei via exec(open(...).read()) ausgeführt wird
if __name__ == "__main__":
    print(f"Created {generate_supplychains()} supply chains.")
