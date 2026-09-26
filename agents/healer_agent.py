from core.data_connector import DataConnector
from core.llm_client import get_llm
from core.state import AgentState

HEAL_SYSTEM = """You fix a broken SQL query. Given the original SQL and the error,
return ONLY the corrected SQL — no prose."""


def healer_node(state: AgentState) -> AgentState:
    state["heal_attempts"] = state.get("heal_attempts", 0) + 1
    state["healed"] = True
    err = "\n".join(state.get("validation_errors") or []) or state.get("error", "")

    # First try executing to capture a real DB error.
    if state.get("validation_passed") and state.get("sql"):
        try:
            dc = DataConnector()
            rows = dc.execute(state["sql"])
            state["data"] = rows
            state["columns"] = list(rows[0].keys()) if rows else []
            state["agents_used"] = state.get("agents_used", []) + ["healer", "executor"]
            return state
        except Exception as e:  # noqa: BLE001
            err = str(e)

    llm = get_llm()
    fixed = llm.complete(HEAL_SYSTEM, f"SQL:\n{state.get('sql','')}\n\nError:\n{err}")
    state["sql"] = fixed.strip().strip("`").replace("```sql", "").replace("```", "")
    state["validation_passed"] = False  # force re-validation
    state["validation_errors"] = []
    state["heal_history"] = state.get("heal_history", []) + [err]
    state["agents_used"] = state.get("agents_used", []) + ["healer"]
    return state
