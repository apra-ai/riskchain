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
        1. For each port, fetch the latest **30 days** of activity.
        2. Calculate the **median** of each metric: portcalls_container, import_container, export_container.
        3. Compare the **most recent value** (latest date) with the **median**:
           - If it deviates by more than **+25% or –25%**, classify it as **anomaly**.
           - High deviation = possible congestion, strike or standstill.
        4. For each anomaly, assess impact and severity. Log only **medium** or **high** risks.
        5. When logging via `create_risk_entry_log`, include:
           - edge_id: {edge_id}
           - source: Include metric and date (e.g., "PortWatch data from 2025-07-25 for Port Singapore")

        Be strict: small fluctuations are **not** risks. Focus on significant anomalies only.""",
        name="logistics_portwatch_risk_agent",
    )
