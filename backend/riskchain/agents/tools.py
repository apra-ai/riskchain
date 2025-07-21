#!/usr/bin/env python3
"""
Generic Risk Creation Tool

This tool can be used by any agent (geopolitical, weather, logistics, environmental, etc.)
to log structured risks into the Django database.
"""

from typing import Dict, Any
from langchain_core.tools import tool
from django.core.exceptions import ValidationError
from supplychains.models import Risk

@tool
def create_risk_entry(name: str, description: str, risk_level: str, risk_score: float = 0.0, source: str = None) -> Dict[str, Any]:
    """
    Create a new Risk entry in the database.

    This tool allows agents to save identified risks with structured metadata.

    Args:
        name: Short name/title of the risk.
        description: Detailed description of the risk.
        risk_level: Risk severity ('low', 'medium', 'high').
        risk_score: Numeric score representing severity (0.0–1.0).
        source: Optional HTTPS URL that links to the source of the information.

    Returns:
        Dictionary with the created risk ID or error message.
    """

    try:
        if source and not source.startswith("https://"):
            raise ValidationError("URL must start with 'https://'")

        risk = Risk.objects.create(
            name=name[:255],
            description=description,
            risk_level=risk_level.lower(),
            risk_score=risk_score,
            source=source
        )
        print("Risk created successfully:")
        print({"name":name[:255],
            "description":description,
            "risk_level":risk_level.lower(),
            "risk_score":risk_score,
            "source":source})

        return {
            "status": "success",
            "risk_id": risk.id,
            "name": risk.name,
            "risk_level": risk.risk_level,
            "risk_score": risk.risk_score
        }

    except Exception as e:
        logger.error(f"Failed to create Risk: {str(e)}")
        return {"status": "error", "message": str(e)}
