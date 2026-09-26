from core.llm_client import get_llm
from core.state import AgentState

EXPLAIN_SYSTEM = """You turn raw query results into a concise, executive-friendly summary.
Use bullet points. Mention the time range and top entities."""


def explainer_node(state: AgentState) -> AgentState:
    # Execute if we haven't already
    if not state.get("data") and state.get("sql") and state.get("validation_passed"):
        try:
            from core.data_connector import DataConnector
            rows = DataConnector().execute(state["sql"])
            state["data"] = rows
            state["columns"] = list(rows[0].keys()) if rows else []
        except Exception as e:  # noqa: BLE001
            state["error"] = str(e)

    if state.get("error") and not state.get("data"):
        state["explanation"] = f"I couldn't complete the query. Details: {state['error']}"
    else:
        llm = get_llm()
        preview = (state.get("data") or [])[:20]
        state["explanation"] = llm.complete(
            EXPLAIN_SYSTEM,
            f"Question: {state['question']}\nRows: {preview}",
        )

    state["agents_used"] = state.get("agents_used", []) + ["explainer"]
    return state
