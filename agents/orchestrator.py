"""
Orchestrator Agent — LangGraph entry point.

Decomposes the user's question into atomic sub-tasks so downstream
agents (schema, memory, semantic, sql) know exactly what to look for.
"""
from __future__ import annotations
import json
import re
import logging

from core.llm_client import get_llm
from core.state import AgentState

log = logging.getLogger("dagger.orchestrator")

SYSTEM_PROMPT = """You are the Orchestrator for a multi-agent data intelligence engine.

Your job: decompose a business question into 2-5 ATOMIC sub-tasks that a
downstream SQL pipeline can execute. Each sub-task must be a single, focused
instruction.

Rules:
- Return ONLY a JSON array of strings. No prose, no markdown fences.
- Each sub-task should mention concrete entities (table/column hints).
- Include time-range resolution as its own sub-task when a date is mentioned.
- Keep sub-tasks under 20 words each.

Example input:
  "Show me top 5 customers by total order value in Q1 2025"

Example output:
  [
    "Identify customer and order tables",
    "Resolve Q1 2025 to date range",
    "Aggregate order value per customer",
    "Sort descending and limit to 5"
  ]
"""


def _parse_tasks(raw: str, fallback: str) -> list[str]:
    """Best-effort parse of the LLM's JSON array. Never crash on bad output."""
    # Strip markdown fences if the model added them anyway
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    # Try to find the first [...] block
    m = re.search(r"\[.*\]", cleaned, re.S)
    if not m:
        return [fallback]

    try:
        tasks = json.loads(m.group(0))
        if isinstance(tasks, list) and all(isinstance(t, str) for t in tasks):
            return tasks[:5]
    except json.JSONDecodeError:
        pass
    return [fallback]


def orchestrator_node(state: AgentState) -> AgentState:
    """LangGraph node: decompose question → sub_tasks, seed agents_used."""
    question = state.get("question", "").strip()
    if not question:
        state["sub_tasks"] = []
        state["error"] = "Empty question."
        return state

    try:
        llm = get_llm()
        raw = llm.complete(SYSTEM_PROMPT, question)
        tasks = _parse_tasks(raw, fallback=question)
    except Exception as e:  # noqa: BLE001
        log.warning("Orchestrator LLM call failed, falling back: %s", e)
        tasks = [question]

    state["sub_tasks"] = tasks
    state["agents_used"] = list(state.get("agents_used", [])) + ["orchestrator"]
    log.info("orchestrator decomposed into %d sub-tasks", len(tasks))
    return state
