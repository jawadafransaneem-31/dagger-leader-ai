"""Dagger Leader entry point — CLI + programmatic API."""
from __future__ import annotations
import json
import sys

from core.langgraph_workflow import compile_workflow
from core.state import AgentState


class QuantumAgent:
    """Public SDK surface."""

    def __init__(self) -> None:
        self._app = compile_workflow()

    def query(self, question: str) -> dict:
        initial: AgentState = {"question": question, "heal_attempts": 0}
        final: AgentState = self._app.invoke(initial)
        return {
            "sql": final.get("sql", ""),
            "data": final.get("data", []),
            "explanation": final.get("explanation", ""),
            "agents_used": final.get("agents_used", []),
            "healed": final.get("healed", False),
            "error": final.get("error"),
        }


def main() -> None:
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = input("Ask a question: ").strip()

    agent = QuantumAgent()
    result = agent.query(question)

    print("\n── Generated SQL ─────────────────────────────")
    print(result["sql"] or "(none)")
    print("\n── Explanation ───────────────────────────────")
    print(result["explanation"] or "(none)")
    print("\n── Meta ──────────────────────────────────────")
    print(json.dumps(
        {"agents_used": result["agents_used"], "healed": result["healed"], "error": result["error"]},
        indent=2,
    ))


if __name__ == "__main__":
    main()
