#!/usr/bin/env python3
"""
Geopolitical Risk Retrieval Tool

This module queries the GDELT API to retrieve real-time news related to geopolitical risks.
It can be used by a multi-agent system to analyze emerging threats.
"""

from typing import Dict, Any
from langchain_core.tools import tool
import requests
from pydantic import ValidationError

from supplychains.models import Risk, Node

@tool
def get_geopolitical_risks(query: str, sourcelang: str = "en", maxrecords: int = 5) -> Dict[str, Any]:
    """
    Retrieve recent geopolitical news articles using the GDELT API.

    This tool queries the GDELT Global Knowledge Graph (GKG) for recent media coverage 
    related to geopolitical risks such as conflicts, political instability, or diplomatic tensions.
    It supports filtering by keyword, language, and number of records.

    Args:
        query: The geopolitical search term (e.g., "Taiwan conflict", "Middle East tensions").
        sourcelang: The source language of the articles (ISO 639-1 code, e.g., "en" for English, "de" for German).
        maxrecords: Maximum number of articles to retrieve (default: 5).

    Returns:
        Dictionary with keys:
        - ``query``: The original search term.
        - ``results``: A list of dictionaries with ``title`` and ``url`` of each article.
        - ``error`` (optional): Error message if the API call fails or returns no results.
    """

    try:
        url = "https://api.gdeltproject.org/api/v2/doc/doc"
        params = {
            "query": query,
            "mode": "artlist",
            "format": "json",
            "sourcelang": sourcelang,
            "maxrecords": maxrecords
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "articles" not in data:
            return {"error": "No articles found."}

        results = [{"title": article.get("title", ""), "url": article.get("url", "")} for article in data["articles"]]
        print("Geopolitical risks retrieved successfully:")
        for article in results:
            print(f"Title: {article['title']}, URL: {article['url']}")

        return {"query": query, "results": results}

    except Exception as e:
        print(f"GDELT API error: {str(e)}")
        return {"error": f"Failed to retrieve geopolitical risks: {str(e)}"}

@tool
def create_risk_entry_geo(name: str, description: str, risk_level: str, risk_score: float = 0.0, url: str = None, node_id: int = None) -> Dict[str, Any]:
    """
    Create a new Risk entry in the database.

    This tool allows agents to save identified risks with structured metadata.

    Args:
        name: Short name/title of the risk.
        description: Detailed description of the risk.
        risk_level: Risk severity ('low', 'medium', 'high').
        risk_score: Numeric score representing severity (0.0–1.0).
        url: HTTPS URL that links to the source of the information.
        node_id: Node ID to associate the risk with a specific node.

    Returns:
        Dictionary with the created risk ID or error message.
    """

    try:
        if url and not url.startswith("https://"):
            raise ValidationError("URL must start with 'https://'")

        risk = Risk.objects.create(
            name=name[:255],
            description=description,
            risk_level=risk_level.lower(),
            risk_score=risk_score,
            url=url,
            source="GDELT API",
            risk_type=0
        )
        print("Risk created successfully:")
        print(f"Name: {name[:255]}, Description: {description}, Risk Level: {risk_level.lower()}, Risk Score: {risk_score}, Url: {url}, Node ID: {node_id}")

        if node_id is not None:
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
        return {"status": "error", "message": str(e)}
