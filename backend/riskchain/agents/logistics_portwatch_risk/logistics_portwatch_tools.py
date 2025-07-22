#!/usr/bin/env python3
"""
Logistics Port Activity Tool

This module queries the IMF PortWatch ArcGIS API to retrieve port-level activity data,
such as vessel counts and regional context. (https://portwatch.imf.org/datasets/acc668d199d1472abaaf2467133d4ca4/api)
It supports structured supply chain analysis by extracting port-specific metrics useful for disruption detection.
"""

from typing import Dict, Any
from langchain_core.tools import tool
import requests

@tool
def get_port_activity_data(max_results: int = 5) -> Dict[str, Any]:
    """
    Retrieve port activity data from PortWatch ArcGIS FeatureServer.

    Args:
        max_results: Maximum number of ports to return. (Default: 5)

    Returns:
        Dictionary with a list of ports and activity metrics:
        - portname
        - country
        - continent
        - vessel_count_total
        - vessel_count_container
        - industry_top1
        - coordinates (lat, lon)
    """

    try:
        url = "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/PortWatch_ports_database/FeatureServer/0/query?where=1%3D1&outFields=portname,country,ISO3,continent,lat,lon,vessel_count_total,vessel_count_container,vessel_count_tanker,industry_top1,portid,vessel_count_RoRo&outSR=4326&f=json"

        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "features" not in data:
            return {"error": "No port data found."}

        results = []
        for feature in data["features"][:max_results]:
            attr = feature["attributes"]
            results.append({
                "port": attr.get("portname", "unknown"),
                "country": attr.get("country", "unknown"),
                "continent": attr.get("continent", "unknown"),
                "vessel_count_total": attr.get("vessel_count_total", 0),
                "vessel_count_container": attr.get("vessel_count_container", 0),
                "industry_top1": attr.get("industry_top1", "unknown"),
                "coordinates": {
                    "lat": attr.get("lat", None),
                    "lon": attr.get("lon", None)
                }
            })

        return {"results": results}

    except Exception as e:
        return {"error": str(e)}