"""
Utility functions for traffic risk agent.
"""

import os
import requests


def geocode_location(location: str) -> tuple[float, float]:
    """
    Converts a city/place name to (latitude, longitude) using HERE Geocoding API.
    """
    api_key = os.getenv("HERE_API_KEY")
    url = "https://geocode.search.hereapi.com/v1/geocode"
    params = {"q": location, "apiKey": api_key}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    if not items:
        raise ValueError(f"No geocoding result for: {location}")
    pos = items[0]["position"]
    return pos["lat"], pos["lng"]

def build_bbox_from_points(p1: tuple[float, float], p2: tuple[float, float]) -> str:
    """
    Returns a bounding box string ("south,west;north,east") from two lat/lon points.
    """
    lat1, lon1 = p1
    lat2, lon2 = p2
    south = min(lat1, lat2)
    north = max(lat1, lat2)
    west = min(lon1, lon2)
    east = max(lon1, lon2)
    return f"{south},{west};{north},{east}"
