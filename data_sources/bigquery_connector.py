from __future__ import annotations
from typing import Any


class BigQueryConnector:
    def __init__(self, project: str) -> None:
        from google.cloud import bigquery
        self._client = bigquery.Client(project=project)

    def execute(self, sql: str) -> list[dict[str, Any]]:
        return [dict(r) for r in self._client.query(sql).result()]

    def list_tables(self) -> list[dict[str, Any]]:
        return [{"table": t.table_id, "schema": t.dataset_id}
                for t in self._client.list_tables(self._client.project)]
