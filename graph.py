"""
LangGraph Orchestrator
----------------------
Wires the 5 agents into a state graph.

Execution order:
    filings -> [news, valuation in parallel] -> risk -> editor -> END

Why a graph instead of a linear script:
- LangGraph manages the shared state automatically.
- It's the same pattern used in production agent systems (Anthropic's Claude
  agents, OpenAI's Swarm, etc.) — recruiters recognize it.
- Easy to extend later: add a "compliance check" agent before editor, or a
  "peer review" loop after editor without rewiring everything.
"""
from langgraph.graph import StateGraph, START, END

from state import ResearchState
from agents.filings import filings_agent
from agents.news import news_agent
from agents.valuation import valuation_agent
from agents.risk import risk_agent
from agents.editor import editor_agent


def build_graph():
    g = StateGraph(ResearchState)

    g.add_node("filings", filings_agent)
    g.add_node("news", news_agent)
    g.add_node("valuation", valuation_agent)
    g.add_node("risk", risk_agent)
    g.add_node("editor", editor_agent)

    # filings must run first (other agents read its output)
    g.add_edge(START, "filings")

    # news and valuation can run in parallel after filings
    g.add_edge("filings", "news")
    g.add_edge("filings", "valuation")

    # risk needs both news and valuation done
    g.add_edge("news", "risk")
    g.add_edge("valuation", "risk")

    # editor runs last
    g.add_edge("risk", "editor")
    g.add_edge("editor", END)

    return g.compile()


graph = build_graph()
