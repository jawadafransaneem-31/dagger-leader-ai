"""Unified data-source interface — Snowflake first, pluggable for others."""
from __future__ import annotations
from typing import Any

from config.settings import get_settings


class DataConnector:
    """Read-only connector. Governance is enforced upstream in sql_guard."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._conn = None

    # ── Connection ─────────────────────────────────────────────
    def connect(self) -> None:
        import snowflake.connector
        s = self._settings
        self._conn = snowflake.connector.connect(
            account=s.snowflake_account,
            user=s.snowflake_user,
            password=s.snowflake_password,
            warehouse=s.snowflake_warehouse,
            database=s.snowflake_database,
            schema=s.snowflake_schema,
        )

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    # ── Introspection ──────────────────────────────────────────
    def list_tables(self) -> list[dict[str, Any]]:
        sql = (
            "SELECT table_schema, table_name, row_count "
            "FROM information_schema.tables "
            "WHERE table_schema NOT IN ('INFORMATION_SCHEMA')"
        )
        return self.execute(sql)

    def describe_table(self, schema: str, table: str) -> list[dict[str, Any]]:
        sql = (
            "SELECT column_name, data_type, is_nullable "
            "FROM information_schema.columns "
            f"WHERE table_schema = '{schema}' AND table_name = '{table}'"
        )
        return self.execute(sql)

    # ── Execution ──────────────────────────────────────────────
    def execute(self, sql: str) -> list[dict[str, Any]]:
        if self._conn is None:
            self.connect()
        cur = self._conn.cursor()
        try:
            cur.execute(sql)
            cols = [c[0] for c in cur.description] if cur.description else []
            rows = cur.fetchall()
            return [dict(zip(cols, r)) for r in rows]
        finally:
            cur.close()
