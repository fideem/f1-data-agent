import pandas as pd

from f1_agent import db


def test_save_table_does_not_duplicate(con_with_laps):
    again = con_with_laps.execute("SELECT * FROM laps").df()
    db.save_table(con_with_laps, "laps", again)
    assert con_with_laps.execute("SELECT count(*) FROM laps").fetchone()[0] == 4


def test_describe_schema_lists_columns(con_with_laps):
    text = db.describe_schema(con_with_laps)
    assert "laps (4 wierszy)" in text
    assert "lap_duration" in text


def test_describe_empty_db(con):
    assert "pusta" in db.describe_schema(con)


def test_save_empty_df_is_noop(con):
    db.save_table(con, "pit", pd.DataFrame())
    assert "pusta" in db.describe_schema(con)
