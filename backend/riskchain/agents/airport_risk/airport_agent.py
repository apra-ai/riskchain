"""Airport Risk Agent Factory"""
from langgraph.prebuilt import create_react_agent
from .airport_tools import get_airport_risks, create_risk_entry_air

def create_airport_risk_agent(llm, edge_id: int, start: str, destination: str):
    """
    Returns a configured Airport Risk Agent.

    Args:
        llm
        edge_id: Edge ID for the risk entry
        start: Start location / airport (e.g. "Frankfurt, Germany")
        destination: Destination location / airport (e.g. "New York, USA")
    """

    return create_react_agent(
        model=llm,
        tools=[get_airport_risks, create_risk_entry_air],
        prompt=f"""You are an airport risk analysis agent assisting in automated supply chain disruption detection.

Your tools:
- `get_airport_risks`: Analyzes real-time delay levels at one or more airports using AeroDataBox.
- `create_risk_entry`: Logs airport-related disruptions with metadata and risk severity.

Your task:
1. Evaluate the following air route:
   - From: **{start}**
   - To: **{destination}**

2. Use `get_airport_risks(start="{start}", destination="{destination}")` to get the current delay info.
3. If delays are `moderate` or `severe`, write a summary of the problem, assign severity, and call `create_risk_entry` with edge_id {edge_id}.
4. Include a valid source (AeroDataBox URL or time-stamped text).

Be accurate, realistic, and avoid speculative entries.
""",
        name="airport_risk_agent",
    )
