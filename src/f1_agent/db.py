"""Warstwa bazy danych: DuckDB w jednym pliku data/f1.duckdb (gotowe).

DuckDB to "SQLite do analityki": baza w pliku, bez serwera, świetnie dogaduje się z pandas.
Agent dostaje dane w tabelach i pisze do nich SQL, czyli dokładnie to, co robisz w pracy.
"""

import duckdb
import pandas as pd

from f1_agent.config import DB_PATH

# Opisy tabel i kolumn, które agent zobaczy w narzędziu describe_tables.
# To ten sam pomysł co opisy tabel pod Databricks Genie: im lepszy opis,
# tym trafniejszy SQL. Uzupełniaj je, gdy dodajesz tabele albo widzisz błędy agenta.
TABLE_DESCRIPTIONS = {
    "sessions": "Sesje (trening, kwalifikacje, wyścig). session_key łączy wszystkie tabele.",
    "drivers": "Kierowcy w danej sesji: driver_number, full_name, name_acronym, team_name.",
    "laps": (
        "Jedno okrążenie jednego kierowcy. lap_duration w sekundach (NULL = brak pomiaru, "
        "np. okrążenie z wypadkiem). is_pit_out_lap = okrążenie wyjazdowe z alei, NIE postój."
    ),
    "stints": (
        "Przejazd na jednym komplecie opon: compound (SOFT/MEDIUM/HARD/INTERMEDIATE/WET), "
        "lap_start, lap_end, tyre_age_at_start (ile okrążeń opona miała na starcie stintu)."
    ),
    "pit": "Postoje w alei serwisowej: lap_number, pit_duration (czas w alei w sekundach).",
    "weather": "Pogoda co ok. minutę: air_temperature, track_temperature, rainfall, wind_speed.",
    "race_control": "Komunikaty dyrekcji: flagi, safety car, kary. category, flag, message.",
}


def connect(path=DB_PATH, read_only: bool = False) -> duckdb.DuckDBPyConnection:
    path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(path), read_only=read_only)


def save_table(con: duckdb.DuckDBPyConnection, name: str, df: pd.DataFrame) -> None:
    """Dopisuje DataFrame do tabeli (tworzy ją, jeśli nie istnieje), bez duplikatów."""
    if df.empty:
        return
    con.register("_incoming", df)
    exists = con.execute(
        "SELECT count(*) FROM information_schema.tables WHERE table_name = ?", [name]
    ).fetchone()[0]
    if exists:
        con.execute(f'INSERT INTO "{name}" SELECT * FROM _incoming EXCEPT SELECT * FROM "{name}"')
    else:
        con.execute(f'CREATE TABLE "{name}" AS SELECT DISTINCT * FROM _incoming')
    con.unregister("_incoming")


def describe_schema(con: duckdb.DuckDBPyConnection) -> str:
    """Zwraca czytelny dla LLM opis wszystkich tabel: opis + kolumny z typami + liczba wierszy."""
    tables = [r[0] for r in con.execute(
        "SELECT table_name FROM information_schema.tables ORDER BY table_name"
    ).fetchall()]
    if not tables:
        return "Baza jest pusta. Najpierw pobierz dane narzędziem fetch_openf1."
    parts = []
    for t in tables:
        cols = con.execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_name = ? ORDER BY ordinal_position", [t]
        ).fetchall()
        n = con.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0]
        col_txt = ", ".join(f"{c} {ty}" for c, ty in cols)
        desc = TABLE_DESCRIPTIONS.get(t, "(brak opisu)")
        parts.append(f"- {t} ({n} wierszy): {desc}\n  kolumny: {col_txt}")
    return "\n".join(parts)
