import pytest
from agents.validator import validator_node


def test_rejects_ddl():
    state = {"sql": "DROP TABLE users;"}
    out = validator_node(state)
    assert out["validation_passed"] is False
    assert any("SELECT" in e or "forbidden" in e.lower() for e in out["validation_errors"])


def test_injects_limit():
    state = {"sql": "SELECT * FROM t"}
    out = validator_node(state)
    assert "LIMIT" in out["sql"].upper()
