#!/usr/bin/env python3
"""
Logistics Port Activity Tool – Daily Port Activity API

This tool retrieves daily port metrics from the IMF PortWatch dataset
(https://portwatch.imf.org/datasets/959214444157458aad969389b3ebe1a0/api),
including portcalls and import/export container volumes.
"""
import traceback
from typing import Dict, Any
from datetime import datetime
import requests
from langchain_core.tools import tool
from pydantic import ValidationError
from supplychains.models import Risk, Node, Edge


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
            "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Daily_Trade_Data/FeatureServer/0/query"
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
        print(f"Portwatch Error: {str(e)}")
        traceback.print_exc()
        return {"error": f"Failed to retrieve logistical activities: {str(e)}"}


@tool
def create_risk_entry_log(name: str,
                          description: str,
                          risk_level: str,
                          risk_score: float = 0.0,
                          source: str = None,
                          edge_id: int = None,
                          node_id: int = None
                          ) -> Dict[str, Any]:
    """
    Create a new Risk entry in the database.

    This tool allows agents to save identified risks with structured metadata.

    Args:
        name: Short name/title of the risk.
        description: Detailed description of the risk.
        risk_level: Risk severity ('low', 'medium', 'high').
        risk_score: Numeric score representing severity (0.0–1.0).
        source: String with Portname, Location and date.
        edge_id: Edge ID to associate the risk with a specific edge.
        node_id: Node ID to associate the risk with a specific node.

    Returns:
        Dictionary with the created risk ID or error message.
    """
    print(f"Creating risk entry: {name[:255]}, "
          f"Description: {description}, "
          f"Risk Level: {risk_level.lower()}, "
          f"Risk Score: {risk_score}, "
          f"Source: {source}, Node ID: {node_id}")
    try:

        risk = Risk.objects.create(
            name=name[:255],
            description=description,
            risk_level=risk_level.lower(),
            risk_score=risk_score,
            source=source,
            url="https://portwatch.imf.org/pages/port-monitor",
            risk_type=2
        )
        print("Risk created successfully:")
        print(f"Name: {name[:255]}, Description: {description}, Risk Level: {risk_level.lower()}, "
              f"Risk Score: {risk_score}, Source: {source}, Node ID: {node_id}")

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
