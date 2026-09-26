from core.sql_generator import _strip_fences


def test_strip_fences():
    assert _strip_fences("```sql\nSELECT 1;\n```") == "SELECT 1;"
    assert _strip_fences("SELECT 1;") == "SELECT 1;"
