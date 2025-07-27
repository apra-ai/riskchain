from geopy.geocoders import Nominatim


def geocode_location(location: str) -> tuple:
    """
    Returns (lat, lon) for a given location string.
    """
    geolocator = Nominatim(user_agent="traffic_agent_geocoder")
    loc = geolocator.geocode(location)
    if loc is None:
        raise ValueError(f"Could not geocode location: {location}")
    return (loc.latitude, loc.longitude)


def build_bbox_from_points(start: tuple, end: tuple, margin: float = 0.2) -> str:
    """
    Build a bounding box with margin around two lat/lon points.
    Returns a bbox string: minLat,minLon,maxLat,maxLon
    """
    lat1, lon1 = start
    lat2, lon2 = end

    min_lat = min(lat1, lat2) - margin
    max_lat = max(lat1, lat2) + margin
    min_lon = min(lon1, lon2) - margin
    max_lon = max(lon1, lon2) + margin

    return f"{min_lat},{min_lon},{max_lat},{max_lon}"
