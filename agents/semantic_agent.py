from config.settings import get_settings
from core.state import AgentState


# Fallback static mappings when Neo4j is unavailable.
DEFAULT_MAPPINGS = {
    "revenue": "SUM(orders.order_value)",
    "q1": "order_date BETWEEN '2025-01-01' AND '2025-03-31'",
    "q2": "order_date BETWEEN '2025-04-01' AND '2025-06-30'",
    "q3": "order_date BETWEEN '2025-07-01' AND '2025-09-30'",
    "q4": "order_date BETWEEN '2025-10-01' AND '2025-12-31'",
}


def semantic_node(state: AgentState) -> AgentState:
    mappings: dict[str, str] = {}
    try:
        from neo4j import GraphDatabase
        s = get_settings()
        drv = GraphDatabase.driver(s.neo4j_uri, auth=(s.neo4j_user, s.neo4j_password))
        with drv.session() as sess:
            for term in state["question"].lower().split():
                rec = sess.run(
                    "MATCH (t:Term {name:$n})-[:MAPS_TO]->(c:Column) "
                    "RETURN c.fqn AS fqn LIMIT 1", n=term
                ).single()
                if rec:
                    mappings[term] = rec["fqn"]
        drv.close()
    except Exception:
        pass

    for k, v in DEFAULT_MAPPINGS.items():
        if k in state["question"].lower():
            mappings.setdefault(k, v)

    state["semantic_mappings"] = mappings
    state["agents_used"] = state.get("agents_used", []) + ["semantic"]
    return state
