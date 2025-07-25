"""Supervisor orchestration for the insurance claim workflow.

This module creates the specialized agents, compiles the LangGraph supervisor,
and exposes a `process_claim_with_supervisor` helper used by the service layer.
"""
from __future__ import annotations

# import logging
import os
from typing import Any, Dict, List

from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
from langgraph_supervisor import create_supervisor

from agents.geopoltical_local_risk.geopolitical_risk_agent import create_geopolitical_risk_agent
from agents.weather_natural_disaster_risk.weather_risk_agent import create_weather_risk_agent
from agents.logistics_portwatch_risk.logistics_portwatch_agent import create_logistics_portwatch_agent
from supplychains.models import Node, Edge
from langchain.schema import HumanMessage, AIMessage
from langchain_core.messages import ToolMessage

load_dotenv()


def _build_llm() -> AzureChatOpenAI:
    """Instantiate AzureChatOpenAI with centralized config."""

    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

    return AzureChatOpenAI(
            azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
            api_key=AZURE_OPENAI_API_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version=AZURE_OPENAI_API_VERSION,
            temperature=0.0,
        )

LLM = _build_llm()

def create_risk_supervisor_node(geopolitical_risk_agent, weather_risk_agent):
    """Create and compile the supervisor coordinating all risk analysis agents."""

    supervisor = create_supervisor(
        agents=[
            geopolitical_risk_agent,
            # environmental_risk_agent,
            weather_risk_agent,
        ],
        model=LLM,
        prompt="""
You are a senior supply chain risk supervisor managing a team of specialized AI agents. Each agent monitors a different risk dimension that may impact a logistics or supply chain node such as a port, airport, or distribution hub.

You receive detailed node data, including:
- Name: [e.g., "Tokyo, Japan"]
- Type: [e.g., "Logistics Port Distribution Hub"]
- Description: [e.g., "Major distribution hub in Japan focused on Logistics Port"]
- Current known risks: [e.g., "Uno Port Standstill"]

Your assigned agents:

1. **Geopolitical & Local Risk Agent** – Monitors regions for political unrest, regulatory changes, strikes, or diplomatic instability that could affect supply chains. Uses real-time data and news sources. Logs medium or high risks via `create_risk_entry` with article links.

2. **Weather & Natural Hazard Agent** – Detects environmental risks such as typhoons, earthquakes, or flooding. Pulls structured data (e.g., USGS) and automatically logs events above critical thresholds (e.g. magnitude ≥ 4.5 or severe weather alerts).

Your responsibilities:
- Trigger appropriate agents based on the node's location and role in the supply chain
- Collect structured, relevant findings per node
- Validate and log all medium or high severity risks into the risk database
- Return a clear, actionable risk report tailored for decision-makers in supply chain governance

Format your output as follows:

---

**RISK_ANALYSIS_COMPLETE**

**NODE:**  
- Name: [e.g., Tokyo, Japan]  
- Type: [e.g., Logistics Port Distribution Hub]  
- Description: [Brief operational role of this node]

**RISK SUMMARY:**  
- Overview of current and emerging geopolitical or environmental risks affecting this location  
- Severity level: [HIGH / MEDIUM / LOW]  
- Geographic scope: [City, region, country]

**RISK DETAILS:**  
- Risk type: [Geopolitical / Earthquake / Typhoon / Other]  
- Description: [Short factual summary]  
- Timeframe: [e.g., Current / Expected / Historical signal]  
- Source: [Link to news or data source]

---

Only report risks that are supported by reliable, real-time or verifiable data. Your insights directly inform operational and procurement strategies.
""").compile()

    return supervisor


def create_risk_supervisor_edge(logistics_portwatch_agent):
    """Create and compile the supervisor coordinating all risk analysis agents."""

    supervisor = create_supervisor(
        agents=[
            logistics_portwatch_agent,
        ],
        model=LLM,
        prompt="""
You are a senior supply chain risk supervisor overseeing a network of AI agents that analyze transportation edges between supply chain nodes. Each edge represents a transport connection (e.g., air cargo, sea freight, trucking) with associated details like time, cost, and mode of transport.

Your AI agents specialize in identifying real-world risks that might affect these transport connections. Your focus is on detecting risks that could disrupt, delay, or increase the cost of specific logistics routes.

Each edge contains:
- From node: [Start location]
- To node: [End location]
- Transport description: [e.g., "Air Cargo to New York"]
- Mode of transportation: [e.g., Plane, Ship, Truck]
- Time of transportation: [e.g., 3 days]
- Cost of transportation: [e.g., 1800.0]

Your responsibilities:
- Trigger relevant agents (e.g., port activity analysis) based on the edge's route and transport mode
- Evaluate whether real-time disruptions (e.g., port congestion, weather delays, strikes) are affecting the route
- Confirm that any medium or high severity risks are logged appropriately
- Return a structured risk assessment per edge that can support operational decisions

Format your output as follows:

---

**RISK_ANALYSIS_COMPLETE**

**EDGE:**  
- From: [Start location]  
- To: [End location]  
- Transport mode: [Plane / Ship / etc.]  
- Description: [Transport description]

**RISK SUMMARY:**  
- Key risks affecting this route  
- Severity level: [HIGH / MEDIUM / LOW]  
- Geographic scope: [Ports, cities, regions affected]

**RISK DETAILS:**  
- Risk type: [Port Congestion / Geopolitical / Weather / etc.]  
- Description: [Short explanation]  
- Timeframe: [e.g., Current, Expected this week]  
- Source: [News link, live API source]

---

Be concise, rely on real-time data sources (e.g. IMF PortWatch), and provide actionable insights for logistics and procurement stakeholders.
""",
    ).compile()

    return supervisor


# ---------------------------------------------------------------------------
# Public helper
# ---------------------------------------------------------------------------
def log_chunk_step(chunk: dict, step_count: int):
    print("\n" + "=" * 60)
    print(f"🧠 Step {step_count}")

    agent_name = list(chunk.keys())[0]
    print(f"🤖 Agent: {agent_name}")

    messages = chunk.get(agent_name, {}).get("messages", "")
    for message in messages:
        if isinstance(message, HumanMessage):
            print("\n💬 Human Messages:")
            content = message.content
            
            if content:
                print("\n📨 Message:")
                print(content)
        elif isinstance(message, ToolMessage):
            print("\n💬 Tool Messages:")
            content = message.content
            
            if content:
                print("\n📨 Message:")
                print(content)
        elif isinstance(message, AIMessage):
            print("\n💬 AI Messages:")
            content = message.content
            additional_kwargs = message.additional_kwargs
            tool_calls = additional_kwargs.get("tool_calls", [])

            if content:
                print("\n📨 Message:")
                print(content)

            for tool_call in tool_calls:
                print("\n🔧 Tool Call:")
                tool_function = tool_call.get("function", {})
                tool_name = tool_function.get("name", "Unknown")
                tool_args = tool_function.get("args", {})

                print(f"Tool: {tool_name}")
                print("Arguments:")
                print(tool_args)

            # if transition := chunk.get("transition"):
            #     print("\n🔄 State Transition:")
            #     print(transition)

    print("=" * 60 + "\n")

def process_node_with_supervisor(node: Node) -> List[Dict[str, Any]]:
    """Run the claim through the supervisor and return detailed trace information.

    Returns comprehensive trace data including:
    - Agent interactions and handoffs
    - Tool calls and results
    - Message history per agent
    - Workflow state transitions
    - Timing information
    """
    # ---------------------------------------------------------------------------
    # Create agents
    # ---------------------------------------------------------------------------

    geopolitical_risk_agent = create_geopolitical_risk_agent(LLM,node.id)
    weather_risk_agent = create_weather_risk_agent(LLM,node.id)


    risk_supervisor = create_risk_supervisor_node(geopolitical_risk_agent, weather_risk_agent)

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
            log_chunk_step(chunk, step_count)
            chunks.append(chunk)

        # logger.info("✅ Workflow completed in %d steps", step_count)
        return chunks
    except Exception as e:
        print("An error occurred during workflow processing:"
              f" {str(e)}")
        traceback.print_exc()
        
        # logger.error("Error in workflow processing: %s", e, exc_info=True)
        raise

def process_edge_with_supervisor(edge: Edge) -> List[Dict[str, Any]]:
    """Run the claim through the supervisor and return detailed trace information.

    Returns comprehensive trace data including:
    - Agent interactions and handoffs
    - Tool calls and results
    - Message history per agent
    - Workflow state transitions
    - Timing information
    """
    # ---------------------------------------------------------------------------
    # Create agents
    # ---------------------------------------------------------------------------

    logistics_portwatch_agent = create_logistics_portwatch_agent(LLM,edge.id)


    risk_supervisor = create_risk_supervisor_edge(logistics_portwatch_agent)

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
                f"from node: {edge.from_node.name}, "
                f"to node: {edge.to_node.name}, "
                f"transport_description: {edge.transport_description}, "
                f"mode of Transportation: {edge.mode}, "
                f"time of Transportation: {edge.time}, "
                f"cost of Transportation: {edge.cost}, "
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
            log_chunk_step(chunk, step_count)
            chunks.append(chunk)

        # logger.info("✅ Workflow completed in %d steps", step_count)
        return chunks
    except Exception as e:
        print("An error occurred during workflow processing:"
              f" {str(e)}")
        traceback.print_exc()
        
        # logger.error("Error in workflow processing: %s", e, exc_info=True)
        raise
