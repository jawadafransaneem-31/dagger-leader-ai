from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from main import QuantumAgent

app = FastAPI(title="Dagger Leader API", version="1.0.0")
_agent = QuantumAgent()


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    sql: str
    data: list
    explanation: str
    agents_used: list[str]
    healed: bool


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    try:
        result = _agent.query(req.question)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e)) from e
    return QueryResponse(**result)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
