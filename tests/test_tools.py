"""Testy narzędzi. Część z nich nie przejdzie, dopóki nie zrobisz TODO 1-4 w tools.py.
Uruchom: uv run pytest -v   i rób po kolei, aż wszystko będzie zielone."""

from f1_agent import tools


def test_describe_tables_tool(con_with_laps):
    text, is_error = tools.execute_tool(con_with_laps, "describe_tables", {})
    assert not is_error
    assert "laps" in text


def test_unknown_tool_is_error(con):
    _, is_error = tools.execute_tool(con, "nie_ma_mnie", {})
    assert is_error


# --- testy do Twoich TODO -------------------------------------------------

def test_all_tools_defined():
    names = {t["name"] for t in tools.TOOLS}
    assert names == {"describe_tables", "run_sql", "fetch_openf1"}


def test_run_sql_select(con_with_laps):
    text, is_error = tools.execute_tool(
        con_with_laps, "run_sql",
        {"sql": "SELECT driver_number, min(lap_duration) AS best FROM laps GROUP BY 1 ORDER BY 1"},
    )
    assert not is_error
    assert "89.1" in text


def test_run_sql_blocks_writes(con_with_laps):
    text, _ = tools.execute_tool(con_with_laps, "run_sql", {"sql": "DROP TABLE laps"})
    assert "laps" in con_with_laps.execute("SHOW TABLES").df()["name"].tolist()
    assert "SELECT" in text


def test_run_sql_error_goes_back_to_model(con_with_laps):
    text, is_error = tools.execute_tool(con_with_laps, "run_sql", {"sql": "SELECT nope FROM laps"})
    assert is_error
    assert "nope" in text
