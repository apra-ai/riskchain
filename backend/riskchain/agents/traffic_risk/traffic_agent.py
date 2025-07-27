"""Road Traffic Agent Factory"""
import os
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from .traffic_utils import geocode_location, build_fixed_bbox
from .traffic_tools import get_traffic_delay_data, create_risk_entry_log

load_dotenv()


def create_traffic_delay_agent(llm, edge_id: int, start: str, end: str):
    """
    Create a LangGraph-based agent to detect traffic disruptions on a road edge.
    """
    start_coords = geocode_location(start)
    end_coords = geocode_location(end)
    bbox = build_fixed_bbox(start_coords, end_coords)

    return create_react_agent(
        model=llm,
        tools=[get_traffic_delay_data, create_risk_entry_log],
        name="logistics_traffic_agent",
        prompt=f"""You are a logistics disruption detection agent for truck transport routes.

Your task is to check for major traffic issues along the road from **{start}** to **{end}**, using TomTom Traffic API.

Your tools:
- `get_traffic_delay_data`: Use this with the bounding box `{bbox}` to get all delays in the region.
- `create_risk_entry_log`: Use this to log **only relevant incidents** that could delay delivery.

Process:
1. Use `get_traffic_delay_data(bbox="{bbox}")`.
2. For each incident returned:
   - If it's a **road closure**, **accident**, or **major construction**, continue.
   - Ignore minor events (low impact, short delays).
3. Classify the impact as:
   - High = closures, long-term disruption → risk_score 0.8–1.0
   - Medium = temporary disruption, active construction → risk_score 0.4–0.7
4. For each relevant event, log it via `create_risk_entry_log` with:
   - name: brief title (e.g., "Road Closure: A8")
   - description: full incident info
   - risk_level: "high" or "medium"
   - risk_score: based on your judgment
   - source: generate a TomTom live map link like `https://plan.tomtom.com/en/?p=lat,lon,10z` using the incident coordinates.
   - edge_id: {edge_id}
   - lat: latitude from incident geometry
   - lon: longitude from incident geometry

Goal: Identify only incidents that realistically threaten on-time delivery across this route.

Be strict. Do **not** log risks for minor traffic events.
"""
    )
