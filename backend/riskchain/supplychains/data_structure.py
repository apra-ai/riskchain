#node
NODE_ROLE_CHOICES = [
    ("SUPPLIER", "Supplier"),
    ("MANUFACTURER", "Manufacturer"),
    ("PLANT", "Plant"),
    ("WAREHOUSE", "Warehouse"),
    ("DISTRIBUTION_CENTER", "Distribution Center"),
    ("PORT", "Port"),
    ("AIRPORT", "Airport"),
    ("CROSSDOCK", "Crossdock"),
    ("CUSTOMER", "Customer"),
]

OWNERSHIP_CHOICES = [
    ("INTERNAL", "Internal"),
    ("3PL", "Third Party Logistics"),
    ("SUPPLIER_OWNED", "Supplier Owned"),
    ("JV", "Joint Venture"),
    ("GOVERNMENT", "Government"),
]

CAPACITY_CLASS_CHOICES = [
    ("LOW", "Low"),
    ("MEDIUM", "Medium"),
    ("HIGH", "High"),
]

#edge
CROSSES_BORDER = [
    ("YES", "Yes"),
    ("NO", "No"),
]

COST_CLASS = [
    ("LOW", "Low"),
    ("MEDIUM", "Medium"),
    ("HIGH", "High"),   
]

RELIABILITY_CLASS = [
    ("LOW", "Low"),
    ("MEDIUM", "Medium"),
    ("HIGH", "High"),
]

DISTANCE_CLASS = [
    ("SHORT", "Short"),
    ("MEDIUM", "Medium"),
    ("LONG", "Long"),
]

TRANSPORT_MODES_CHOICES = [
    ("ROAD", "Road"),
    ("RAIL", "Rail"),
    ("AIR", "Air"),
    ("SEA", "Sea"),
    ("INLAND_WATERWAY", "Inland Waterway"),
]