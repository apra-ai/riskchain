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
            temperature=0.1,
        )

LLM = _build_llm()

def create_risk_supervisor(geopolitical_risk_agent, weather_risk_agent, logistics_portwatch_agent):
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
            weather_risk_agent,
            logistics_portwatch_agent,
        ],
        model=LLM,
        prompt="""
You are a senior risk manager supervising a team of AI risk analysis agents. Your role is to coordinate the evaluation of supply chain risks across multiple dimensions and deliver actionable risk assessments to human decision-makers.

Your agents:

1. **Geopolitical & Local Risk Agent** – Identifies risks from political instability, conflict, diplomatic tensions, or regional unrest. It uses real-time media coverage and structured signals to detect relevant risks. If the agent evaluates a risk as MEDIUM or HIGH, it must create a risk entry using its `create_risk_entry` tool and include the article source URL.

2. **Weather & Natural Disaster Risk Agent** – Evaluates natural hazards such as earthquakes that may disrupt supply chains. It queries external data (e.g., USGS) and automatically logs risks for affected locations if they meet defined magnitude thresholds (≥ 4.5).

3. **Logistics Port Activity Agent – Monitors port-level activity from IMF PortWatch, such as high vessel or container traffic. Detects signs of congestion or logistic slowdowns that could impact shipping lanes.

Your responsibilities:
- Trigger the agents based on the user's query, location, or supply chain asset
- Ensure each agent returns structured and relevant findings
- Validate that risks with medium or high severity are correctly logged to the database
- Summarize both geopolitical, natural hazard and logistic port risks for decision-makers in a clear, actionable format


End your analysis in the following format:

---

**RISK_ANALYSIS_COMPLETE**

**RISK SUMMARY:**
- Concise overview of geopolitical and environmental risk signals
- Affected countries, cities, or supply chain nodes
- Brief priority assessment

**RISK DETAILS:**
- Risk level: [HIGH / MEDIUM / LOW]
- Risk type: [Geopolitical / Earthquake / Other Natural Hazard]
- Risk description: [Short explanation]
- Source: [News article or scientific data link]

**STRATEGIC IMPACT:**
- How the risk could impact supply chains, suppliers, or transport routes
- Implications for cost, delays, or operational stability

**RECOMMENDATIONS:**
- Suggested mitigation or monitoring actions
- Whether to escalate to risk governance or crisis response teams

---

Your output supports high-stakes decisions in procurement, logistics, and supply chain risk governance. Be precise, structured, and only report risks supported by real-time or verifiable data.""",
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
    logistics_portwatch_agent = create_logistics_portwatch_agent(LLM, node.id)


    risk_supervisor = create_risk_supervisor(geopolitical_risk_agent, weather_risk_agent, logistics_portwatch_agent)

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
        # logger.error("Error in workflow processing: %s", e, exc_info=True)
        raise
