"""Supervisor orchestration for the insurance claim workflow.

This module creates the specialized agents, compiles the LangGraph supervisor,
and exposes a `process_claim_with_supervisor` helper used by the service layer.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_anthropic import ChatAnthropic
from langgraph_supervisor import create_supervisor

from agents.geopoltical_local_risk.geopolitical_risk_agent import create_geopolitical_risk_agent
from supplychains.models import Node, Edge

load_dotenv()


# def _build_llm() -> AzureChatOpenAI:
#     """Instantiate AzureChatOpenAI with centralized config."""
#     from app.core.config import get_settings

#     settings = get_settings()
#     endpoint = settings.azure_openai_endpoint
#     deployment = settings.azure_openai_deployment_name or "gpt-4o"
#     api_key = settings.azure_openai_api_key

#     logger.info("✅ Configuration loaded successfully")
#     logger.info("Azure OpenAI Endpoint: %s", endpoint or "Not set")
#     logger.info("Deployment Name: %s", deployment)
#     logger.info("API Key configured: %s", "Yes" if api_key else "No")

#     return AzureChatOpenAI(
#             azure_deployment=deployment,
#             api_key=api_key,
#             azure_endpoint=endpoint,
#             api_version="2024-08-01-preview",
#             temperature=0.1,
#         )

# LLM = _build_llm()

CLAUDE_MODEL = "claude-3-7-sonnet-20250219"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

LLM = ChatAnthropic(
    model=CLAUDE_MODEL,
    temperature=0.1,
    api_key=ANTHROPIC_API_KEY,
    max_tokens=4096,
)

# ---------------------------------------------------------------------------
# Create specialized agents
# ---------------------------------------------------------------------------

geopolitical_risk_agent = create_geopolitical_risk_agent(LLM)

# ---------------------------------------------------------------------------
# Compile supervisor
# ---------------------------------------------------------------------------


def create_risk_supervisor():
    """Create and compile the supervisor coordinating all risk analysis agents."""

#     prompt_finished = """You are a senior risk manager supervising a team of AI risk analysis agents. Your role is to coordinate the evaluation of supply chain risks across multiple dimensions and deliver actionable risk assessments to human decision-makers.

# Your team consists of:
# 1. Geopolitical & Local Risk Agent – Identifies risks from political instability, conflict, or regional unrest
# 2. Environmental Risk Agent – Assesses pollution, regulation, and environmental compliance risks
# 3. Logistics Disruption Agent – Detects transport or infrastructure-related supply chain disruptions
# 4. Weather & Natural Disaster Agent – Monitors and flags risks from extreme weather or natural hazards

# Your responsibilities:
# - Coordinate and trigger the agents based on the context or query
# - Aggregate their findings and validate the completeness of the analysis
# - Ensure all medium or high risks are entered into the risk database via each agent’s `create_risk_entry` tool
# - Present a clear, structured summary for decision-makers

# You must end your analysis in the following format:

# RISK_ANALYSIS_COMPLETE

# RISK SUMMARY:
# - Concise overview of major risk signals detected
# - Priority regions or topics with elevated risk levels

# RISK BREAKDOWN:
# - [Agent Name]: [Short summary of identified risk or "No significant risk"]
#   - Risk level: [HIGH/MEDIUM/LOW]
#   - Relevant article or data source: [URL]

# STRATEGIC IMPACT:
# - How these risks could affect supply chains, sourcing, or logistics
# - Supply chain nodes or partners likely to be affected
# - Potential impact on cost, delays, or compliance

# RECOMMENDATIONS:
# - Mitigation steps or monitoring suggestions
# - Which areas require immediate attention
# - If relevant, propose escalation to internal risk governance teams

# Your output should support strategic decisions in procurement, logistics, or supply chain operations. Accuracy, clarity, and explainability are essential."""

    supervisor = create_supervisor(
        agents=[
            geopolitical_risk_agent,
            # environmental_risk_agent,
            # logistics_disruption_agent,
            # weather_disaster_agent,
        ],
        model=LLM,
        prompt="""
You are a senior risk manager supervising an AI risk analysis agent. Your role is to coordinate the evaluation of geopolitical and local risks that may impact supply chains and deliver actionable insights to human decision-makers.

Your agent:
1. Geopolitical & Local Risk Agent – Identifies risks from political instability, conflict, diplomatic tensions, or regional unrest. It uses real-time media coverage and structured signals to detect relevant risks. If the agent evaluates a risk as MEDIUM or HIGH, it must create a risk entry using its `create_risk_entry` tool and include the article source URL.

Your responsibilities:
- Trigger the Geopolitical & Local Risk Agent based on the user’s query
- Validate the relevance and completeness of the analysis
- Ensure any detected risk with medium or high severity is saved to the database
- Deliver a structured, clear summary of geopolitical risks for decision-makers

End your analysis in the following format:

RISK_ANALYSIS_COMPLETE

RISK SUMMARY:
- Concise overview of geopolitical risk signals detected
- Priority countries, regions, or issues

RISK DETAILS:
- Risk level: [HIGH / MEDIUM / LOW]
- Risk description: [Short explanation]
- Source: [Article or media URL used as input]

STRATEGIC IMPACT:
- How this risk could affect supply chains, suppliers, or transport routes
- Implications for cost, delivery times, or operational reliability

RECOMMENDATIONS:
- Suggested mitigation or monitoring actions
- Whether the issue should be escalated to a risk governance team

Your output supports strategic decisions in procurement, logistics, and supply chain management. Your insights must be well-structured, clear, and grounded in the underlying data.""",
    ).compile()

    return supervisor


risk_supervisor = create_risk_supervisor()


# ---------------------------------------------------------------------------
# Public helper
# ---------------------------------------------------------------------------


def process_edge_with_supervisor(node: Node) -> List[Dict[str, Any]]:
    """Run the claim through the supervisor and return detailed trace information.

    Returns comprehensive trace data including:
    - Agent interactions and handoffs
    - Tool calls and results
    - Message history per agent
    - Workflow state transitions
    - Timing information
    """

    # logger.info("")
    # logger.info("🚀 Starting supervisor-based claim processing…")
    # logger.info("📋 Processing Claim ID: %s",
    #             claim_data.get("claim_id", "Unknown"))
    # logger.info("%s", "=" * 60)

    messages = [
        {
            "role": "user",
            "content": (
                "Please process this claim through your team of specialists:"
                f"name: {node.name}, "
                f"type: {node.type}, "
                f"description: {node.description}, "
            ),
        }
    ]

    chunks: List[Dict[str, Any]] = []
    step_count = 0

    # Enhanced streaming with detailed trace capture
    try:
        for chunk in risk_supervisor.stream(
            {"messages": messages},
            stream_mode="updates",  # Get individual node updates instead of full state
            debug=False  # Disable debug information temporarily
        ):
            step_count += 1
            chunks.append(chunk)

        # logger.info("✅ Workflow completed in %d steps", step_count)
        return chunks
    except Exception as e:
        # logger.error("Error in workflow processing: %s", e, exc_info=True)
        raise