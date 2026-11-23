import pandas as pd
import pytest

from f1_agent import db


@pytest.fixture
def con(tmp_path):
    """Pusta baza DuckDB w katalogu tymczasowym (testy nie ruszają data/f1.duckdb)."""
    c = db.connect(tmp_path / "test.duckdb")
    yield c
    c.close()


@pytest.fixture
def con_with_laps(con):
    laps = pd.DataFrame({
        "session_key": [9693] * 4,
        "driver_number": [4, 4, 1, 1],
        "lap_number": [1, 2, 1, 2],
        "lap_duration": [90.5, 89.1, 91.0, None],
        "is_pit_out_lap": [False, False, False, False],
    })
    db.save_table(con, "laps", laps)
    return con
