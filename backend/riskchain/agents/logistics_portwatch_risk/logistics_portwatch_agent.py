"""Logistics Port Agent Factory"""
from langgraph.prebuilt import create_react_agent

from .logistics_portwatch_tools import get_port_activity_data, create_risk_entry_log


def create_logistics_portwatch_agent(llm, edge_id: int):
    """Return a configured Logistical Activity Risk agent.

    Args:
        llm: An instantiated LangChain LLM shared by the app.
        edge_id: The edge ID to associate with risk entries.
    """
    return create_react_agent(
        model=llm,
        tools=[get_port_activity_data, create_risk_entry_log],
        prompt=f"""You are a logistics disruption detection agent. Your task is to analyze a full shipping route consisting of multiple ports (not just origin and destination) to detect disruptions in global supply chains.

        Your tools:
        - `get_port_activity_data`: Returns container traffic data (import/export/portcalls) for a specific port.
        - `create_risk_entry_log`: Creates a structured risk report based on abnormal port activity.

        Your task:
        1. For a given route (a list of ports), call `get_port_activity_data` for **each** port.
        2. Analyze the metrics for each port in the route critically to detect potential logistics risks such as:
           - sudden drops in import/export container volumes
           - high portcall counts suggesting congestion
           - complete standstills or abnormal activity patterns
        3. For each anomaly you identify, assess the potential supply chain impact and classify the risk level as `high`, `medium`, or `low`.
        4. **If a risk is assessed as **`medium`**, call `create_risk_entry_log` to register it in the system.
        5. **IMPORTANT:** When calling `create_risk_entry_log`, you **must include a reference to the metric anomaly and date** as the `source` field (e.g., "PortWatch data from 2025-07-21, Port Name ___, Country ___.").
        6. **IMPORTANT:** When calling `create_risk_entry_log`, you **must include the edge_id:{edge_id}** as the `edge_id` field to ensure proper traceability.

        Always explain your reasoning clearly, avoid speculation, and focus 
        on delivering actionable insights for supply chain managers.""",
        name="logistics_portwatch_risk_agent",
    )
