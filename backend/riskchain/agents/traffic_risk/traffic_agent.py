"""Road Traffic Agent Factory"""
import os
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from .traffic_utils import geocode_location, build_bbox_from_points
from .traffic_tools import get_traffic_delay_data, create_risk_entry_log

load_dotenv()

def create_traffic_delay_agent(llm, edge_id: int, start: str, end: str):
    """
    Create a LangGraph-based agent to detect traffic disruptions on a road edge.
    """
    api_key = os.getenv("TOMTOM_API_KEY")
    start_coords = geocode_location(start)
    end_coords = geocode_location(end)
    bbox = build_bbox_from_points(start_coords, end_coords, margin=0.1)  # 0.1 statt 0.2

    return create_react_agent(
        model=llm,
        tools=[get_traffic_delay_data, create_risk_entry_log],
        name="logistics_traffic_agent",
        prompt=f"""
You are a traffic disruption agent checking the route from **{start}** to **{end}** (edge_id: {edge_id}).

Step-by-step:
1. Call get_traffic_delay_data(bbox="{bbox}")
2. For each result:
   - Only process incidents with high or medium impact.
   - Classify risk:
     - "high" → closures, long-term issues → 0.8–1.0
     - "medium" → temp. construction/disruption → 0.4–0.7
3. Log each incident with create_risk_entry_log(name, description, risk_level, risk_score, source, lat, lon, edge_id).

TomTom links use:
https://plan.tomtom.com/en/?p=<lat>,<lon>,10z

Only create risk entries if the incident is truly impactful for the route!
        """
    )