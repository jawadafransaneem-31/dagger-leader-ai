import pytest
from main import QuantumAgent


@pytest.mark.slow
def test_end_to_end_query():
    agent = QuantumAgent()
    result = agent.query("Show me top 5 customers by total order value in Q1 2025")
    assert "sql" in result
    assert isinstance(result["agents_used"], list)
