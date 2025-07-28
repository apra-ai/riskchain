"""Utility functions for road traffic analysis."""
from typing import Tuple
from geopy.geocoders import Nominatim


def geocode_location(location: str) -> Tuple[float, float]:
    """
    Geocode a city/location string into latitude and longitude.

    Args:
        location: Location name (e.g., "Berlin")

    Returns:
        (lat, lon)
    """
    geolocator = Nominatim(user_agent="riskchain_agent", timeout=10)
    loc = geolocator.geocode(location)
    if not loc:
        raise ValueError(f"Location not found: {location}")
    return (loc.latitude, loc.longitude)


def build_fixed_bbox(start: Tuple[float, float], end: Tuple[float, float], margin: float = 0.2) -> str:
    """
    Build a bounding box around two coordinates, extended by a margin.

    Args:
        start: (lat, lon)
        end: (lat, lon)
        margin: Margin in degrees to extend around min/max coordinates

    Returns:
        Bbox string: "minLat,minLon,maxLat,maxLon"
    """
    min_lat = min(start[0], end[0]) - margin
    max_lat = max(start[0], end[0]) + margin
    min_lon = min(start[1], end[1]) - margin
    max_lon = max(start[1], end[1]) + margin

    return f"{min_lat},{min_lon},{max_lat},{max_lon}"
