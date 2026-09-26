"""LangGraph definition wiring all eight agents together."""
from __future__ import annotations

from langgraph.graph import END, StateGraph

from core.state import AgentState


def build_graph() -> StateGraph:
    # Lazy imports keep module load light and avoid circular deps.
    from agents.orchestrator import orchestrator_node
    from agents.schema_agent import schema_node
    from agents.memory_agent import memory_node
    from agents.semantic_agent import semantic_node
    from agents.sql_agent import sql_node
    from agents.validator import validator_node
    from agents.healer_agent import healer_node
    from agents.explainer_agent import explainer_node

    g = StateGraph(AgentState)

    g.add_node("orchestrator", orchestrator_node)
    g.add_node("schema", schema_node)
    g.add_node("memory", memory_node)
    g.add_node("semantic", semantic_node)
    g.add_node("sql", sql_node)
    g.add_node("validator", validator_node)
    g.add_node("healer", healer_node)
    g.add_node("explainer", explainer_node)

    g.set_entry_point("orchestrator")
    g.add_edge("orchestrator", "schema")
    g.add_edge("schema", "memory")
    g.add_edge("memory", "semantic")
    g.add_edge("semantic", "sql")
    g.add_edge("sql", "validator")

    # Conditional: PASS → explainer, FAIL → healer
    g.add_conditional_edges(
        "validator",
        lambda s: "pass" if s.get("validation_passed") else "fail",
        {"pass": "explainer", "fail": "healer"},
    )

    # Healer loops back to validator, or bails to explainer on retry exhaustion
    g.add_conditional_edges(
        "healer",
        lambda s: "retry" if s.get("heal_attempts", 0) < 3 and s.get("sql") else "give_up",
        {"retry": "validator", "give_up": "explainer"},
    )

    g.add_edge("explainer", END)
    return g


def compile_workflow():
    return build_graph().compile()
