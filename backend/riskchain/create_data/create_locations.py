from supplychains.models import City, Country

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

for country in countries_cities:
    country_obj, created_country = Country.objects.get_or_create(name=country)
    if not created_country:
        print(f"Didnt create country {country}")
    for city in countries_cities[country]:
        city_obj, created_city = City.objects.get_or_create(name=city, country=country_obj)
        if not created_city:
            print(f"Didnt create city {city} in country {country}")

# 72 Cities in 13 countries created.