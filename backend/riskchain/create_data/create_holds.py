# python manage.py shell

import random
from django.utils import timezone
from supplychains.models import Node, Hold

# --- Parameter ---
TOTAL_HOLDS = 200        # wie viele Holds insgesamt erzeugen
SEED = 42                # für Reproduzierbarkeit (optional)
USE_REUSE_PROB = 0.0     # z.B. 0.3: manchmal Typ/Severity von existierendem Hold des Nodes übernehmen

rng = random.Random(SEED)

nodes = list(Node.objects.all())
if not nodes:
    raise SystemExit("Keine Nodes vorhanden.")

HOLD_TYPES = [k for k, _ in Hold.HOLD_TYPE_CHOICES]
SEVERITIES = [1, 2, 3, 4, 5]

to_create = []

for i in range(TOTAL_HOLDS):
    node = rng.choice(nodes)  # Auswahl MIT Zurücklegen

    # Optional: manchmal bestehenden Hold dieses Nodes als Vorlage nehmen
    if USE_REUSE_PROB > 0 and rng.random() < USE_REUSE_PROB and node.holds.exists():
        tpl = node.holds.order_by("?").first()  # schnell & bequem
        hold_type = tpl.hold_type
        severity = tpl.severity
    else:
        hold_type = rng.choice(HOLD_TYPES)
        severity = rng.choice(SEVERITIES)

    to_create.append(Hold(
        node=node,
        hold_type=hold_type,
        severity=severity,
        # created_at setzt auto_now_add automatisch, sonst:
        # created_at=timezone.now(),
    ))

# Schnell anlegen
Hold.objects.bulk_create(to_create, batch_size=1000)
print(f"✅ {len(to_create)} Holds erzeugt (mit Zurücklegen über {len(nodes)} Nodes).")
