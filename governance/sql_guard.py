"""Standalone guardrails usable outside the agent pipeline (e.g. API layer)."""
from __future__ import annotations
import logging
import time
from functools import wraps

from config.settings import get_settings

log = logging.getLogger("dagger.governance")

FORBIDDEN = ("insert", "update", "delete", "drop", "create", "alter", "truncate", "grant", "revoke")


def assert_read_only(sql: str) -> None:
    low = sql.lower()
    if not (low.lstrip().startswith("select") or low.lstrip().startswith("with")):
        raise PermissionError("Only SELECT/WITH queries are permitted.")
    for kw in FORBIDDEN:
        if kw in low:
            raise PermissionError(f"Forbidden keyword: {kw.upper()}")


def enforce_limit(sql: str, max_rows: int | None = None) -> str:
    s = get_settings()
    cap = max_rows or s.max_rows
    if "limit" not in sql.lower():
        sql = sql.rstrip(";") + f"\nLIMIT {cap};"
    return sql


def with_timeout(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        s = get_settings()
        start = time.time()
        result = fn(*args, **kwargs)
        elapsed = time.time() - start
        if elapsed > s.query_timeout_seconds:
            log.warning("Query exceeded timeout: %.2fs", elapsed)
        log.info("query executed in %.2fs", elapsed)
        return result
    return wrapper


def audit(event: str, **fields) -> None:
    log.info("audit event=%s fields=%s", event, fields)
