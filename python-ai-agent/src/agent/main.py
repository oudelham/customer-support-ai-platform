from __future__ import annotations

from langgraph.graph import StateGraph, START, END

from src.agent.state import AgentState
from src.agent.nodes.intent_classifier import classify_intent
from src.agent.nodes.specialists import run_specialist, run_analysis


def route_intent(state: AgentState) -> str:
    return "specialist"


async def specialist_node(state: AgentState):
    return await run_specialist(state)


async def analysis_node(state: AgentState):
    return await run_analysis(state)


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("intent_classifier", classify_intent)
    graph.add_node("specialist", specialist_node)
    graph.add_node("analysis", analysis_node)

    graph.add_edge(START, "intent_classifier")
    graph.add_conditional_edges(
        "intent_classifier",
        route_intent,
        {"specialist": "specialist"},
    )
    graph.add_edge("specialist", "analysis")
    graph.add_edge("analysis", END)

    return graph.compile()


agent_graph = build_graph()
