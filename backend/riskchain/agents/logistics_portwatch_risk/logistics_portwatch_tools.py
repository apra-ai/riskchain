#!/usr/bin/env python3
"""
Logistics Port Activity Tool – Daily Port Activity API

This tool retrieves daily port metrics from the IMF PortWatch dataset
(https://portwatch.imf.org/datasets/959214444157458aad969389b3ebe1a0/api),
including portcalls and import/export container volumes.
"""

from typing import Dict, Any
from datetime import datetime
import requests
from langchain_core.tools import tool


@tool
def get_port_activity_data(
    country: str = None,
    portname: str = None,
    maxresults: int = 10
) -> Dict[str, Any]:
    """
    Retrieve current daily port activity data from the PortWatch API.

    Args:
        country: Optional country name to filter ports (e.g., "Germany").
        portname: Optional port name to filter results (e.g., "Hamburg").
        maxresults: Max number of records to return (default: 10)

    Returns:
        Dictionary with a list of port metrics:
        - date
        - portname
        - country
        - portcalls_container
        - import_container
        - export_container
    """
    try:
        url = (
            "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest"
            "/services/Daily_Trade_Data/FeatureServer/0/query"
        )

        conditions = []
        if country:
            conditions.append(f"country = '{country}'")
        if portname:
            conditions.append(f"portname = '{portname}'")
        where_clause = " AND ".join(conditions) if conditions else "1=1"

        params = {
            "where": where_clause,
            "outFields": ",".join([
                "date", "portname", "country",
                "portcalls_container", "import_container", "export_container"
            ]),
            "orderByFields": "date DESC",
            "resultRecordCount": maxresults,
            "f": "json"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "features" not in data:
            return {"error": "No port activity data found."}

        results = []
        for feature in data["features"]:
            attr = feature["attributes"]
            timestamp = attr.get("date")
            readable_date = (
                datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d")
                if timestamp else "unknown"
            )

            results.append({
                "date": readable_date,
                "port": attr.get("portname", "unknown"),
                "country": attr.get("country", "unknown"),
                "portcalls_container": attr.get("portcalls_container", 0),
                "import_container": attr.get("import_container", 0),
                "export_container": attr.get("export_container", 0)
            })

        return {"results": results}

    except Exception as e:
        print(f"Error creating risk entry: {str(e)}")
        return {"status": "error", "message": str(e)}
