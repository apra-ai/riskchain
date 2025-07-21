#!/usr/bin/env python3
"""
Geopolitical Risk Retrieval Tool

This module queries the GDELT API to retrieve real-time news related to geopolitical risks.
It can be used by a multi-agent system to analyze emerging threats.
"""

from typing import Dict, Any
from langchain_core.tools import tool
import requests

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
        print({"query": query, "results": results})
        
        return {"query": query, "results": results}

    except Exception as e:
        logger.error(f"GDELT API error: {str(e)}")
        return {"error": f"Failed to retrieve geopolitical risks: {str(e)}"}