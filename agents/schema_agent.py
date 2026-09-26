from core.data_connector import DataConnector
from core.state import AgentState


def schema_node(state: AgentState) -> AgentState:
    dc = DataConnector()
    try:
        tables = dc.list_tables()
    except Exception:
        tables = []
    # Naive keyword filter; production version uses ChromaDB similarity.
    q = state["question"].lower()
    relevant = [t for t in tables if any(w in t.get("table_name", "").lower() for w in q.split())]
    state["relevant_tables"] = relevant or tables[:8]
    state["agents_used"] = state.get("agents_used", []) + ["schema"]
    return state
