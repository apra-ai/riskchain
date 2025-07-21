"""Geopolitical & local risk agent factory."""
from langgraph.prebuilt import create_react_agent

from .tools import *

def geopolitical_local_risk_agent(llm):
    """Return a configured Geopolitical & local risk agent agent.

    Args:
        llm: An instantiated LangChain LLM shared by the app.
    """
    prompt_agent = \
"""prompt here"""

    return create_react_agent(
        model=llm,
        tools=[],
        prompt=prompt_agent,
        name="geopolitical_local_risk_agent",
    )