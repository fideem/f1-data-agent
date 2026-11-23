"""Ewaluacja agenta (weekend 2). Mierzy, jak często agent odpowiada poprawnie i ile to kosztuje.

Plan (TODO, zrób w kolejny weekend):
  1. Uzupełnij evals/questions.jsonl do ~15-20 pytań. Oczekiwane odpowiedzi policz
     SAMA SQL-em w notebooku (to jest Twoja "prawda", tzw. ground truth).
  2. Dla każdego pytania: result = run_agent(q["question"], verbose=False)
  3. Oceń: czy q["expected"] występuje w result.answer (check == "contains").
     Później możesz dodać ocenę liczbową z tolerancją albo LLM-as-judge.
  4. Zbierz tabelę: id, poprawne?, steps, liczba wywołań narzędzi, błędy narzędzi, koszt.
  5. Wypisz podsumowanie: accuracy, średni koszt i średnią liczbę kroków; zapisz do
     evals/results.csv. Te liczby trafią do README i do CV.
Uwaga: to woła prawdziwe API, więc kosztuje. Zacznij od 3 pytań.
"""

import json
from pathlib import Path

QUESTIONS = Path(__file__).with_name("questions.jsonl")


def load_questions() -> list[dict]:
    return [json.loads(line) for line in QUESTIONS.read_text().splitlines() if line.strip()]


if __name__ == "__main__":
    raise NotImplementedError("Weekend 2: ewaluacja, patrz docstring")
