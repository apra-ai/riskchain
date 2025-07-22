from langchain_core.tools import tool
from geopy.geocoders import Nominatim
import requests
from datetime import datetime
from supplychains.models import Risk, Node

@tool
def get_earthquakes_near_location(location_name: str, radius_km: float = 100, min_magnitude: float = 4.5, node_id: int = None) -> dict:
    """
    Retrieve recent earthquakes near a given location using the USGS Earthquake API.

    Args:
        location_name: Name of the location (e.g., "Tokyo, Japan").
        radius_km: Search radius in kilometers (default: 100).
        min_magnitude: Minimum earthquake magnitude to filter (default: 4.5).
        node_id: Node ID to associate the risk with a specific node.

    Returns:
        Dictionary containing:
        - location: Full location string from geocoding.
        - earthquakes: List of recent earthquakes with magnitude, time, and coordinates.
        - error (optional): Error message if geocoding or API fails.
    """

    # Step 1: Geocode the location name
    geolocator = Nominatim(user_agent="earthquake-risk-agent")
    location = geolocator.geocode(location_name)

    if not location:
        return {"error": f"Could not find coordinates for '{location_name}'."}

    lat, lon = location.latitude, location.longitude

    # Step 2: Build USGS API query
    usgs_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "latitude": lat,
        "longitude": lon,
        "maxradiuskm": radius_km,
        "minmagnitude": min_magnitude,
        "orderby": "time",
        "limit": 10
    }

    response = requests.get(usgs_url, params=params)
    response.raise_for_status()
    data = response.json()

    print(f"Found {len(data.get('features', []))} earthquakes near {location_name}.")

    earthquakes = []
    for feature in data.get("features", []):
        prop = feature["properties"]
        geometry = feature["geometry"]
        time_ms = prop.get("time")
        time_str = datetime.utcfromtimestamp(time_ms / 1000).strftime('%Y-%m-%d %H:%M:%S UTC') if time_ms else None
        earthquakes.append({
            "magnitude": prop.get("mag"),
            "place": prop.get("place"),
            "time": time_str,
            "coordinates": geometry.get("coordinates"),
            "url": prop.get("url")
        })

    for eq in earthquakes:
        magnitude = eq["magnitude"]
        place = eq["place"]
        time = eq["time"]

        if magnitude < 5:
            continue
        elif magnitude < 6.0:
            risk_level = "medium"
            risk_score = 0.5
        else:
            risk_level = "high"
            risk_score = 0.8

        risk = Risk.objects.create(
            name=f"Earthquake at {place}",
            description=f"Earthquake detected with magnitude {magnitude} at {place} for the time {time}",
            risk_level=risk_level.lower(),
            risk_score=risk_score,
            source=eq["url"],
            risk_type=3
        )
        print(f"Risk created: {risk.name}, Level: {risk_level}, Score: {risk_score}")
        print(f"Earthquake: {magnitude} at {place} on {time}")
        if node_id is not None:
            node = Node.objects.get(id=node_id)
            node.risks.add(risk)

    return {
        "location": location.address,
        "latitude": lat,
        "longitude": lon,
        "earthquakes": earthquakes
    }

    # except Exception as e:
    #     print(f"Error retrieving earthquakes: {str(e)}")
    #     return {"error": str(e)}
