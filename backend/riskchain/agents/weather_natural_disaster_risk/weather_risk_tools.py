from langchain_core.tools import tool
from geopy.geocoders import Nominatim
import requests
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime
import xml.etree.ElementTree as ET
from supplychains.models import Risk, Node
import traceback


# @tool
# def get_earthquakes_near_location(location_name: str, radius_km: float = 100, min_magnitude: float = 4.5, node_id: int = None) -> dict:
#     """
#     Retrieve recent earthquakes near a given location using the USGS Earthquake API.

#     Args:
#         location_name: Name of the location (e.g., "Tokyo, Japan").
#         radius_km: Search radius in kilometers (default: 100).
#         min_magnitude: Minimum earthquake magnitude to filter (default: 4.5).
#         node_id: Node ID to associate the risk with a specific node.

#     Returns:
#         Dictionary containing:
#         - location: Full location string from geocoding.
#         - earthquakes: List of recent earthquakes with magnitude, time, and coordinates.
#         - error (optional): Error message if geocoding or API fails.
#     """
#     try:
#         # Step 1: Geocode the location name
#         geolocator = Nominatim(user_agent="earthquake-risk-agent")
#         location = geolocator.geocode(location_name)

#         if not location:
#             return {"error": f"Could not find coordinates for '{location_name}'."}

#         lat, lon = location.latitude, location.longitude

#         # Step 2: Build USGS API query
#         usgs_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
#         params = {
#             "format": "geojson",
#             "latitude": lat,
#             "longitude": lon,
#             "maxradiuskm": radius_km,
#             "minmagnitude": min_magnitude,
#             "orderby": "time",
#             "limit": 10
#         }

#         response = requests.get(usgs_url, params=params)
#         response.raise_for_status()
#         data = response.json()

#         print(f"Found {len(data.get('features', []))} earthquakes near {location_name}.")

#         earthquakes = []
#         for feature in data.get("features", []):
#             prop = feature["properties"]
#             geometry = feature["geometry"]
#             time_ms = prop.get("time")
#             time_str = datetime.utcfromtimestamp(time_ms / 1000).strftime('%Y-%m-%d %H:%M:%S UTC') if time_ms else None
#             earthquakes.append({
#                 "magnitude": prop.get("mag"),
#                 "place": prop.get("place"),
#                 "time": time_str,
#                 "coordinates": geometry.get("coordinates"),
#                 "url": prop.get("url")
#             })

#         for eq in earthquakes:
#             magnitude = eq["magnitude"]
#             place = eq["place"]
#             time = eq["time"]

#             if magnitude < 5:
#                 continue
#             elif magnitude < 6.0:
#                 risk_level = "medium"
#                 risk_score = 0.5
#             else:
#                 risk_level = "high"
#                 risk_score = 0.8

#             risk = Risk.objects.create(
#                 name=f"Earthquake at {place}",
#                 description=f"Earthquake detected with magnitude {magnitude} at {place} for the time {time}",
#                 risk_level=risk_level.lower(),
#                 risk_score=risk_score,
#                 source=eq["url"],
#                 risk_type=3
#             )
#             print(f"Risk created: {risk.name}, Level: {risk_level}, Score: {risk_score}")
#             print(f"Earthquake: {magnitude} at {place} on {time}")
#             if node_id is not None:
#                 node = Node.objects.get(id=node_id)
#                 node.risks.add(risk)

#         return {
#             "location": location.address,
#             "latitude": lat,
#             "longitude": lon,
#             "earthquakes": earthquakes
#         }

#     except Exception as e:
#         print(f"Error retrieving earthquakes: {str(e)}")
#         return {"error": str(e)}

@tool
def get_disasters_near_location(location_name: str, radius_km: float = 500, node_id: int = None) -> dict:
    """
    Retrieve recent disasters (earthquakes, floods, tropical cyclones) near a location using the GDACS API.

    Args:
        location_name: Name of the location (e.g., "Jakarta, Indonesia").
        radius_km: Radius in kilometers to search for disasters (default: 500).
        node_id: Optional Node ID to link the risk to a specific node.

    Returns:
        Dictionary containing:
        - location: Full geocoded location.
        - disasters: List of disasters near the location.
        - error: Optional error message.
    """
    try:
        geolocator = Nominatim(user_agent="gdacs-risk-agent")
        location = geolocator.geocode(location_name)

        if not location:
            print(f"Could not find coordinates for '{location_name}'.")
            return {"error": f"Could not find coordinates for '{location_name}'."}

        lat, lon = float(location.latitude), float(location.longitude)

        gdacs_url = "https://www.gdacs.org/xml/rss.xml"
        response = requests.get(gdacs_url)
        response.raise_for_status()

        root = ET.fromstring(response.content)

        namespaces = {
            "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#",  # für <geo:lat> / <geo:long>
            "gdacs": "http://www.gdacs.org",
            "dc": "http://purl.org/dc/elements/1.1/",
        }

        disasters = []
        for item in root.findall(".//item"):
            lat_elem = item.find(".//geo:lat", namespaces)
            lon_elem = item.find(".//geo:long", namespaces)

            print("Found item in GDACS feed:")
            print(f"Processing item: {item.find('title').text}")

            latitude = lat_elem.text if lat_elem is not None else "N/A"
            longitude = lon_elem.text if lon_elem is not None else "N/A"

            # Haversine distance check
            def haversine(lat1, lon1, lat2, lon2):
                R = 6371
                dlat = radians(lat2 - lat1)
                dlon = radians(lon2 - lon1)
                a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))
                return R * c

            distance_km = haversine(lat, lon, float(latitude), float(longitude))
            print(f"Distance from {location_name} to disaster: {distance_km:.2f} km")
            if distance_km > radius_km:
                continue
            
            title = item.find("title").text
            description = item.find("description").text
            link = item.find("link").text

            event_type = item.find("gdacs:eventtype", namespaces).text
            alert_level = item.find("gdacs:alertlevel", namespaces).text

            disasters.append({
                "type": event_type,
                "name": title,
                "alert_level": alert_level,
                "distance_km": round(distance_km, 1),
                "url": link
            })

            if alert_level.lower() in ["green","orange", "red"]:
                risk_level = "low"
                risk_score = 0.2
                risk_level = "high" if alert_level.lower() == "red" else "medium"
                risk_score = 0.8 if alert_level.lower() == "red" else 0.5

                risk = Risk.objects.create(
                    name=f"{event_type} near {location_name}",
                    description=f"{event_type} reported by GDACS: {title} ({alert_level}) approx. {round(distance_km)}km from {location_name}",
                    risk_level=risk_level,
                    risk_score=risk_score,
                    source=link,
                    risk_type=3  # Environmental / Natural Disaster
                )
                print(f"Risk created: {risk.name}, Level: {risk_level}, Score: {risk_score}")
                if node_id is not None:
                    node = Node.objects.get(id=node_id)
                    node.risks.add(risk)

        return {
            "location": location.address,
            "latitude": lat,
            "longitude": lon,
            "disasters": disasters
        }

    except Exception as e:
        print(f"Error retrieving disasters: {str(e)}")
        traceback.print_exc()
        return {"error": str(e)}