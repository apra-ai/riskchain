"""
Road Traffic Activity Tool – Daily Road Traffic API
This tool retrieves real-time traffic metrics from the HERE dataset (here.com).
"""

import traceback
from typing import Dict, Any
import requests
from langchain_core.tools import tool
from supplychains.models import Risk, Edge, Node

HERE_TRAFFIC_URL = "https://traffic.ls.hereapi.com/traffic/6.3/incidents.json"

def build_here_traffic_url(lat: float, lon: float) -> str:
    """Returns a clickable traffic map URL centered at given coordinates."""
    return f"https://wego.here.com/traffic/explore?map={lat},{lon},11,traffic"

def bbox_center(bbox: str) -> tuple[float, float]:
    """Returns the center latitude and longitude of a bounding box."""
    lat1, lon1, lat2, lon2 = map(float, bbox.replace(';', ',').split(','))
    return (lat1 + lat2) / 2, (lon1 + lon2) / 2


@tool
def get_traffic_delay_data(bbox: str, api_key: str, max_results: int = 50) -> Dict[str, Any]:
    """Retrieve current traffic incident data from HERE API within a bounding box."""
    try:
        params = {
            "apikey": api_key,
            "bbox": bbox,
            "language": "en",
            "maxresults": max_results
        }
        response = requests.get(HERE_TRAFFIC_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        items = data.get("TRAFFICITEMS", {}).get("TRAFFICITEM", [])
        results = []
        center_lat, center_lon = bbox_center(bbox)

        for item in items:
            incident_url = build_here_traffic_url(center_lat, center_lon)

            results.append({
                "type": item.get("TRAFFICITEMTYPEDESC", "unknown"),
                "description": item.get("COMMENTS", {}).get("value", "no description"),
                "criticality": item.get("CRITICALITY", {}).get("DESCRIPTION", "unknown"),
                "start_time": item.get("STARTTIME"),
                "end_time": item.get("ENDTIME"),
                "source_url": incident_url
            })

        return {"results": results}

    except Exception as e:
        print(f"Traffic Tool Error: {str(e)}")
        traceback.print_exc()
        return {"error": f"Failed to retrieve traffic data: {str(e)}"}


@tool
def create_risk_entry_log(name: str,
                          description: str,
                          risk_level: str,
                          risk_score: float = 0.0,
                          source: str = None,
                          edge_id: int = None,
                          node_id: int = None
                          ) -> Dict[str, Any]:
    """Create a new Risk entry in the database."""
    try:
        risk = Risk.objects.create(
            name=name[:255],
            description=description,
            risk_level=risk_level.lower(),
            risk_score=risk_score,
            source=source,
            url="https://developer.here.com/products/traffic",
            risk_type=4
        )

        if edge_id is not None:
            edge = Edge.objects.get(id=edge_id)
            edge.risks.add(risk)
            edge.save()
        elif node_id is not None:
            node = Node.objects.get(id=node_id)
            node.risks.add(risk)
            node.save()

        return {
            "status": "success",
            "risk_id": risk.id,
            "name": risk.name,
            "risk_level": risk.risk_level,
            "risk_score": risk.risk_score
        }

    except Exception as e:
        print(f"Error creating risk entry: {str(e)}")
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
