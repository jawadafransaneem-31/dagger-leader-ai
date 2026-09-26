from config.settings import get_settings
from core.state import AgentState

FORBIDDEN = ("insert", "update", "delete", "drop", "create", "alter", "truncate", "grant")


def validator_node(state: AgentState) -> AgentState:
    sql = (state.get("sql") or "").strip()
    errs: list[str] = []

    low = sql.lower()
    if not low.startswith("select") and not low.startswith("with"):
        errs.append("Query must be SELECT/WITH only.")
    for kw in FORBIDDEN:
        if kw in low:
            errs.append(f"Forbidden keyword detected: {kw.upper()}")

    # Auto-inject LIMIT
    s = get_settings()
    if "limit" not in low:
        sql = sql.rstrip(";") + f"\nLIMIT {s.max_rows};"
        state["sql"] = sql

    state["validation_passed"] = not errs
    state["validation_errors"] = errs
    state["agents_used"] = state.get("agents_used", []) + ["validator"]
    return state
