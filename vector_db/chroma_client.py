from __future__ import annotations
from config.settings import get_settings


def get_schema_collection():
    import chromadb
    s = get_settings()
    client = chromadb.PersistentClient(path=s.chroma_persist_dir)
    return client.get_or_create_collection(s.chroma_collection_name)


def index_schema(table: str, summary: str, metadata: dict | None = None) -> None:
    col = get_schema_collection()
    col.upsert(ids=[table], documents=[summary], metadatas=[metadata or {}])


def search_schema(query: str, k: int = 5) -> list[dict]:
    col = get_schema_collection()
    res = col.query(query_texts=[query], n_results=k)
    out = []
    for doc, meta in zip(res.get("documents", [[]])[0], res.get("metadatas", [[]])[0]):
        out.append({"summary": doc, **(meta or {})})
    return out
