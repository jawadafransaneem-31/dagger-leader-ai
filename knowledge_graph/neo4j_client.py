from __future__ import annotations
from config.settings import get_settings


class Neo4jClient:
    def __init__(self) -> None:
        from neo4j import GraphDatabase
        s = get_settings()
        self._drv = GraphDatabase.driver(s.neo4j_uri, auth=(s.neo4j_user, s.neo4j_password))

    def close(self) -> None:
        self._drv.close()

    def upsert_term(self, term: str, column_fqn: str) -> None:
        with self._drv.session() as s:
            s.run(
                "MERGE (t:Term {name:$t}) "
                "MERGE (c:Column {fqn:$c}) "
                "MERGE (t)-[:MAPS_TO]->(c)",
                t=term, c=column_fqn,
            )

    def lookup(self, term: str) -> str | None:
        with self._drv.session() as s:
            rec = s.run(
                "MATCH (t:Term {name:$t})-[:MAPS_TO]->(c:Column) "
                "RETURN c.fqn AS fqn LIMIT 1", t=term,
            ).single()
            return rec["fqn"] if rec else None
