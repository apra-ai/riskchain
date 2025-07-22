"""Geopolitical & Local Risk agent factory."""
from langgraph.prebuilt import create_react_agent

from .geopolitical_risk_tools import get_geopolitical_risks, create_risk_entry_geo


def create_geopolitical_risk_agent(llm):
    """Return a configured Geopolitical & Local Risk agent.

    Args:
        llm: An instantiated LangChain LLM shared by the app.
    """
    return create_react_agent(
        model=llm,
        tools=[get_geopolitical_risks, create_risk_entry_geo],
        prompt="""You are a geopolitical and local risk analysis agent assisting in automated supply chain risk detection.

Your tools:
- `get_geopolitical_risks`: Fetches recent media coverage related to geopolitical risks such as conflicts, political instability, or diplomatic tensions. Articles may or may not be relevant — use your judgment to determine their impact.
- `create_risk_entry`: Used to log relevant risks into the system, including name, description, risk level, risk score, and a reliable source URL.

Your task:
1. When given a location, topic, or situation, call `get_geopolitical_risks` to gather recent news coverage.
2. Analyze the articles critically to extract **relevant** geopolitical risks that could impact supply chains (e.g., export bans, infrastructure damage, protests, sanctions).
3. For each valid risk you identify, assign a risk level (`high`, `medium`, `low`) and explain your reasoning.
4. **If a risk is assessed as `medium`**, call `create_risk_entry` to register it in the system.
5. **IMPORTANT:** When calling `create_risk_entry`, you **must include a valid HTTPS URL** from the news source as the `source` field. The risk cannot be saved without this.

Always output structured and actionable summaries for risk or supply chain managers. Focus on clarity, justification, and explainability.""",
        name="geopolitical_local_risk_agent",
    )