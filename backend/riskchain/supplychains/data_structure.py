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

TRANSPORT_MODES_CHOICES = [
    ("ROAD", "Road"),
    ("RAIL", "Rail"),
    ("AIR", "Air"),
    ("SEA", "Sea"),
    ("INLAND_WATERWAY", "Inland Waterway"),
]




countries_cities = {
    "USA": [
        "New York", "Los Angeles", "Chicago", "Houston", "Atlanta"
    ],
    "CANADA": [
        "Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa"
    ],
    "MEXICO": [
        "Mexico City", "Monterrey", "Guadalajara", "Puebla", "Querétaro"
    ],
    "BRAZIL": [
        "São Paulo", "Rio de Janeiro", "Brasília", "Curitiba", "Porto Alegre"
    ],
    "UK": [
        "London", "Manchester", "Birmingham", "Liverpool", "Glasgow"
    ],
    "FRANCE": [
        "Paris", "Lyon", "Marseille", "Toulouse", "Lille"
    ],
    "GERMANY": [
        "Berlin", "Hamburg", "Munich", "Frankfurt am Main", "Cologne",
        "Stuttgart", "Düsseldorf", "Leipzig", "Nuremberg", "Bremen",
        "Hannover", "Dresden"
    ],
    "ITALY": [
        "Rome", "Milan", "Turin", "Naples", "Bologna"
    ],
    "SPAIN": [
        "Madrid", "Barcelona", "Valencia", "Seville", "Bilbao"
    ],
    "CHINA": [
        "Beijing", "Shanghai", "Shenzhen", "Guangzhou", "Chengdu"
    ],
    "JAPAN": [
        "Tokyo", "Osaka", "Nagoya", "Yokohama", "Fukuoka"
    ],
    "INDIA": [
        "Mumbai", "Delhi", "Bengaluru", "Chennai", "Hyderabad"
    ],
    "AUSTRALIA": [
        "Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"
    ]
}