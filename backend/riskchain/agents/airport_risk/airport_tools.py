"""
Airport Delay Risk Tool
This Module analyzes airport delays using AeroDataBox API to identify potential risks for supply chains.
(https://rapidapi.com/aedbx-aedbx/api/aerodatabox/playground)
"""
import time
from typing import Dict, Any, Optional
from langchain_core.tools import tool
import requests
from datetime import datetime
from supplychains.models import Risk
from dotenv import load_dotenv
import os

load_dotenv()
AERODATABOX_API_KEY = os.getenv("AERODATABOX_API_KEY")
AERODATABOX_HOST = "aerodatabox.p.rapidapi.com"

def resolve_location_to_icao(query: str) -> Optional[str]:
    """
    Resolves a city name or airport term to its ICAO code using AeroDataBox.

    Args:
        query: A location string like "Frankfurt, Germany"

    Returns:
        ICAO code (e.g. "EDDF") or None
    """
    try:
        url = f"https://{AERODATABOX_HOST}/airports/search/term"
        headers = {
            "X-RapidAPI-Key": AERODATABOX_API_KEY,
            "X-RapidAPI-Host": AERODATABOX_HOST
        }
        params = {"q": query}
        time.sleep(1.1)  # Rate limiting
        res = requests.get(url, headers=headers, params=params)
        res.raise_for_status()
        items = res.json().get("items", [])
        if not items:
            return None
        return items[0]["icao"]
    except Exception as e:
        print(f"resolve_location_to_icao error for '{query}': {e}")
        return None

@tool
def get_airport_risks(start: str = None, destination: str = None, icao_code: str = None) -> Dict[str, Any]:
    """
    Analyzes the delay status of an airport using AeroDataBox.

    Args:
        start: Start location (city or airport name)
        destination: Destination location (city or airport name)
        icao_code: Optional direct ICAO code

    Returns:
        Dictionary with delay info per airport
    """

    if not AERODATABOX_API_KEY:
        return {"error": "API key not set."}
    if not any([start, destination, icao_code]):
        return {"error": "Provide at least one: start, destination, or icao_code."}

    codes = []
    if icao_code:
        codes.append(icao_code)
    else:
        if start:
            icao = resolve_location_to_icao(start)
            if icao:
                codes.append(icao)
        if destination:
            icao = resolve_location_to_icao(destination)
            if icao:
                codes.append(icao)

    results = []
    for code in codes:
        try:
            url = f"https://{AERODATABOX_HOST}/airports/icao/{code}/delays"
            headers = {
                "X-RapidAPI-Key": AERODATABOX_API_KEY,
                "X-RapidAPI-Host": AERODATABOX_HOST
            }
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            results.append({
                "icao": code,
                "timestamp": datetime.utcnow().isoformat(),
                "delays": res.json()
            })
        except Exception as e:
            results.append({
                "icao": code,
                "error": str(e)
            })

    return {"results": results}

@tool
def create_risk_entry_air(name: str, description: str, risk_level: str, risk_score: float = 0.0,
                          source: str = None, edge_id: int = None) -> Dict[str, Any]:
    """
    Create a new Risk entry in the database (airport-specific), associated with a transport edge.

    Args:
        name: Short name/title of the risk.
        description: Detailed description of the risk.
        risk_level: Risk severity ('low', 'medium', 'high').
        risk_score: Numeric score (0.0–1.0)
        source: AeroDataBox-Link or timestamped text as source.
        edge_id: edge ID to associate this risk with a transport edge.

    Returns:
        Success message with risk ID or error details.
    """
    try:
        if not source:
            source = "https://aerodatabox.p.rapidapi.com/"
        risk = Risk.objects.create(
            name=name[:255],
            description=description,
            risk_level=risk_level.lower(),
            risk_score=risk_score,
            url=source,
            source="AeroDataBox",
            risk_type=5
        )
        if edge_id is not None:
            from supplychains.models import Edge
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
        return {"status": "error", "message": str(e)}
