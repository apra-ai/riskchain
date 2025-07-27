"""
Road Traffic Activity Tool – Daily Road Traffic API
This tool retrieves real-time traffic metrics from the TOMTOM dataset (https://www.tomtom.com/).
"""
import os
import requests
import traceback
from langchain_core.tools import tool
from supplychains.models import Risk, Edge

TOMTOM_TRAFFIC_URL = "https://api.tomtom.com/traffic/services/5/incidentDetails"

@tool
def get_traffic_delay_data(bbox: str, max_results: int = 50) -> dict:
    """
    Fetch traffic delays from TomTom Traffic API within a bounding box.

    Args:
        bbox: Bounding box string in format "minLat,minLon,maxLat,maxLon"
        max_results: Max number of incidents to return

    Returns:
        Dictionary with traffic incidents
    """
    try:
        api_key = os.getenv("TOMTOM_API_KEY")
        if not api_key:
            raise ValueError("Missing TOMTOM_API_KEY")

        params = {
            "key": api_key,
            "bbox": bbox,
            #"fields": "id,geometry,properties",
            #"language": "en",
            #"categoryFilter": "accident,roadClosure",
            "maxResults": max_results
        }

        response = requests.get(TOMTOM_TRAFFIC_URL, params=params, timeout=10)
        response.raise_for_status()

        return {"results": response.json().get("incidents", [])}

    except requests.HTTPError as e:
        return {
            "error": f"HTTP error: {e}",
            "status_code": response.status_code,
            "response_text": response.text,
            "params": params
        }
    except Exception as e:
        traceback.print_exc()
        return {"error": f"Unhandled error: {str(e)}"}


@tool
def create_risk_entry_log(name: str,
                          description: str,
                          risk_level: str,
                          risk_score: float = 0.0,
                          source: str = None,
                          lat: float = None,
                          lon: float = None,
                          edge_id: int = None) -> dict:
    """Create a new Risk entry in the database."""
    try:
        source = source or (
            f"https://plan.tomtom.com/en/?p={lat},{lon},10z" if lat and lon else None
        )

        risk = Risk.objects.create(
            name=name[:255],
            description=description,
            risk_level=risk_level.lower(),
            risk_score=risk_score,
            source=source,
            url="https://plan.tomtom.com/en/",
            risk_type=4
        )

        if edge_id:
            edge = Edge.objects.get(id=edge_id)
            edge.risks.add(risk)
            edge.save()

        return {
            "status": "success",
            "risk_id": risk.id,
            "name": risk.name,
            "risk_level": risk.risk_level,
            "risk_score": risk.risk_score
        }

    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": str(e)}