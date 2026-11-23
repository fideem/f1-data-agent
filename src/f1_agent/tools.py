"""Narzędzia agenta: definicje dla Claude (JSON Schema) + funkcje Pythona, które je wykonują.

Jak to działa (tool calling):
  1. Wysyłasz do Claude listę TOOLS: nazwa, opis, schemat parametrów.
  2. Claude sam decyduje, czy i które narzędzie wywołać, i zwraca blok `tool_use`
     z nazwą i argumentami (np. {"sql": "SELECT ..."}).
  3. TY uruchamiasz odpowiednią funkcję w Pythonie (execute_tool) i odsyłasz wynik
     jako `tool_result`. Model nigdy sam nie wykonuje kodu, tylko prosi o wykonanie.

Gotowe: describe_tables (wzór do naśladowania), execute_tool, format_df.
Do zrobienia przez Ciebie: TODO 1-4 poniżej.
"""

import json

import pandas as pd

from f1_agent import db, openf1

MAX_ROWS_TO_MODEL = 50  # nie wysyłamy modelowi tysięcy wierszy: to drogie i niepotrzebne


# ---------------------------------------------------------------------------
# Definicje narzędzi widoczne dla modelu
# ---------------------------------------------------------------------------

DESCRIBE_TABLES_TOOL = {
    "name": "describe_tables",
    "description": (
        "Zwraca listę tabel w bazie DuckDB z opisem, kolumnami, typami i liczbą wierszy. "
        "Wywołaj to przed pisaniem SQL, żeby znać dokładne nazwy kolumn."
    ),
    "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
}

# TODO 1: zdefiniuj narzędzie run_sql.
#   - name: "run_sql"
#   - description: napisz dla modelu, co robi (wykonuje JEDNO zapytanie SELECT w DuckDB
#     i zwraca max 50 wierszy) i kiedy go używać. Opis to część promptu: model czyta go
#     dosłownie, więc pisz konkretnie (np. że czasy są w sekundach).
#   - input_schema: obiekt z jednym wymaganym polem "sql" typu string.
#   Podpowiedź: wzoruj się na DESCRIBE_TABLES_TOOL, dodaj "properties" i "required".
RUN_SQL_TOOL = None

# TODO 2: zdefiniuj narzędzie fetch_openf1, które pobiera dane z OpenF1 do bazy.
#   - parametry: "endpoint" (string, enum = posortowana lista openf1.ALLOWED_ENDPOINTS)
#     oraz "params" (obiekt z filtrami, np. {"session_key": 9693}).
#   - w opisie wyjaśnij, że wynik ląduje w tabeli o nazwie endpointu i że trzeba potem
#     użyć run_sql. Dopisz przykład: najpierw sessions z year i session_name, żeby
#     znaleźć session_key.
#   Podpowiedź: enum w JSON Schema to {"type": "string", "enum": [...]}.
FETCH_OPENF1_TOOL = None

TOOLS = [t for t in (DESCRIBE_TABLES_TOOL, RUN_SQL_TOOL, FETCH_OPENF1_TOOL) if t is not None]


# ---------------------------------------------------------------------------
# Implementacje
# ---------------------------------------------------------------------------

def format_df(df: pd.DataFrame) -> str:
    """Zamienia DataFrame na krótki tekst dla modelu (max MAX_ROWS_TO_MODEL wierszy)."""
    if df.empty:
        return "Zapytanie nie zwróciło żadnych wierszy."
    head = df.head(MAX_ROWS_TO_MODEL)
    note = f"\n(pokazano {len(head)} z {len(df)} wierszy)" if len(df) > len(head) else ""
    return head.to_csv(index=False) + note


def describe_tables(con) -> str:
    return db.describe_schema(con)


def run_sql(con, sql: str) -> str:
    """TODO 3: wykonaj zapytanie i zwróć wynik jako tekst.

    Kroki:
      a) Bezpieczeństwo: przepuść tylko zapytania zaczynające się od SELECT albo WITH
         (po .strip().lower()). Inaczej zwróć tekst błędu, np. "Błąd: dozwolony tylko SELECT".
         Dlaczego: agent nie powinien móc zrobić DROP TABLE.
      b) Wykonaj: con.execute(sql).df()  -> DataFrame
      c) Zwróć format_df(df).
    Nie łap tu wyjątków duckdb: execute_tool zamieni je na tool_result z is_error=True,
    a model zobaczy treść błędu i sam poprawi SQL. To kluczowa cecha agenta!
    """
    raise NotImplementedError("TODO 3: run_sql")


def fetch_openf1(con, endpoint: str, params: dict | None = None) -> str:
    """TODO 4: pobierz dane z OpenF1 i zapisz do tabeli o nazwie endpointu.

    Kroki:
      a) df = openf1.fetch(endpoint, **(params or {}))
      b) db.save_table(con, endpoint, df)
      c) Zwróć krótkie podsumowanie dla modelu: ile wierszy, jakie kolumny
         (NIE całe dane, model doczyta je przez run_sql).
    """
    raise NotImplementedError("TODO 4: fetch_openf1")


_HANDLERS = {
    "describe_tables": lambda con, args: describe_tables(con),
    "run_sql": lambda con, args: run_sql(con, args["sql"]),
    "fetch_openf1": lambda con, args: fetch_openf1(con, args["endpoint"], args.get("params")),
}


def execute_tool(con, name: str, args: dict) -> tuple[str, bool]:
    """Uruchamia narzędzie po nazwie. Zwraca (tekst_wyniku, czy_błąd).

    Błąd nie wywraca programu: wraca do modelu jako tool_result z is_error=True.
    """
    handler = _HANDLERS.get(name)
    if handler is None:
        return f"Nieznane narzędzie: {name}", True
    try:
        return handler(con, args), False
    except NotImplementedError:
        raise  # to Twoje TODO, chcemy je od razu zobaczyć
    except Exception as e:  # noqa: BLE001 - każdy błąd narzędzia oddajemy modelowi
        return f"Błąd {type(e).__name__}: {e}", True


def to_json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)
