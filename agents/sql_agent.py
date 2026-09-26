from core.sql_generator import generate_sql
from core.state import AgentState


def sql_node(state: AgentState) -> AgentState:
    sql = generate_sql(
        question=state["question"],
        tables=state.get("relevant_tables", []),
        mappings=state.get("semantic_mappings", {}),
        past_examples=state.get("past_queries", []),
    )
    state["sql"] = sql
    state["agents_used"] = state.get("agents_used", []) + ["sql"]
    return state
