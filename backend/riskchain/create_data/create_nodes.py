from supplychains.data_structure import NODE_ROLE_CHOICES, OWNERSHIP_CHOICES, CAPACITY_CLASS_CHOICES
from supplychains.models import Node, City
from random import randint

for city in City.objects.all():
    node_roles = [i for i in range(len(NODE_ROLE_CHOICES))]
    for _ in range(2):
        random_choice = randint(0, len(node_roles) - 1)
        role_value = NODE_ROLE_CHOICES[random_choice][0]
        node_roles.pop(random_choice)
        ownership_value = OWNERSHIP_CHOICES[randint(0, len(OWNERSHIP_CHOICES) - 1)][0]
        capacity_value = CAPACITY_CLASS_CHOICES[randint(0, len(CAPACITY_CLASS_CHOICES) - 1)][0]
        Node.objects.get_or_create(
            country=city.country,
            city=city,
            node_role=role_value,
            ownership=ownership_value,
            capacity_class=capacity_value
        )

print("✅ 2 Nodes pro City erstellt.")