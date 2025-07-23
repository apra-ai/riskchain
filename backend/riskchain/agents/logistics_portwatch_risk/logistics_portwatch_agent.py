"""
Logistics Port Agent Factory

This agent uses IMF PortWatch data to analyze global port activity
and detect potential supply chain risks such as congestion, limited throughput,
or unusual vessel patterns.
"""

from langgraph.prebuilt import create_react_agent
from logistics_portwatch_tools import get_port_activity_data


def create_logistics_port_agent(llm, node_id: int):
    """Return a configured Logistical Portwatch agent.

    Args:
        llm: An instantiated LangChain LLM shared by the app.
    """
    return create_react_agent(
        model=llm,
        tools=[get_port_activity_data],
        prompt=f"""You are a logistics intelligence agent specialized in global port monitoring.
Your data source is the IMF PortWatch ArcGIS API, providing real-time information about vessel activity and container traffic at ports worldwide.

Your available tool:
- `get_port_activity_data`: Retrieves daily port metrics. You can use optional filters:
  - `country` (e.g., "Germany")
  - `portname` (e.g., "Hamburg")
  - `maxresults` (default: 10)

Your responsibilities:
1. Use the tool to retrieve current port data based on the region, country, or port specified.
2. Look for signs of logistical disruptions such as unusual congestion, significant increase/decrease in container traffic, or abnormal portcalls.
3. If applicable, compare activity levels to detect spikes or slowdowns.
4. Assess the impact level as HIGH, MEDIUM, or LOW and explain your reasoning based on the data.
5. If a noteworthy anomaly exists, reference `node_id:{node_id}` to allow traceability in the system.
6. Summarize findings for decision-makers clearly and concisely, focusing on operational relevance for global supply chains.

Avoid speculation, rely strictly on the available data, and structure your conclusions for clarity and strategic use.
""",
        name="logistics_port_agent",
    )
