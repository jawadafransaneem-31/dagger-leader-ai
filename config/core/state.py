"""Shared state passed between agents in the LangGraph pipeline."""
from __future__ import annotations
from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    # Input
    question: str

    # Orchestrator
    sub_tasks: list[str]

    # Schema Agent
    relevant_tables: list[dict[str, Any]]

    # Memory Agent
    past_queries: list[dict[str, Any]]

    # Semantic Agent
    semantic_mappings: dict[str, str]

    # SQL Agent
    sql: str

    # Validator
    validation_passed: bool
    validation_errors: list[str]

    # Healer
    heal_attempts: int
    healed: bool
    heal_history: list[str]

    # Execution
    data: list[dict[str, Any]]
    columns: list[str]

    # Explainer
    explanation: str

    # Metadata
    agents_used: list[str]
    error: str | None
