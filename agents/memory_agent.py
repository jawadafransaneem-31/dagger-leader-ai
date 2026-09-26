from config.settings import get_settings
from core.state import AgentState


def memory_node(state: AgentState) -> AgentState:
    try:
        import chromadb
        s = get_settings()
        client = chromadb.PersistentClient(path=s.chroma_persist_dir)
        col = client.get_or_create_collection("query_history")
        res = col.query(query_texts=[state["question"]], n_results=3)
        past = [
            {"question": q, "sql": m.get("sql", "")}
            for q, m in zip(res.get("documents", [[]])[0], res.get("metadatas", [[]])[0])
        ]
    except Exception:
        past = []
    state["past_queries"] = past
    state["agents_used"] = state.get("agents_used", []) + ["memory"]
    return state
