"""Logowanie zużycia tokenów i kosztu każdego zapytania (gotowe).

Każde wywołanie API dopisuje wiersz do logs/usage.csv. To jest surowiec do drugiego
projektu: "koszt tokenów AI vs zaoszczędzony czas pracy".
"""

import csv
from datetime import UTC, datetime

from f1_agent.config import LOG_DIR

# Ceny w USD za 1 mln tokenów (cennik Anthropic, stan na 11.2026).
# Sprawdź aktualne ceny na https://www.anthropic.com/pricing zanim opiszesz wyniki w README.
PRICES = {
    "claude-opus-5-5": {"input": 4.00, "output": 20.00, "cache_read": 0.20},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00, "cache_read": 0.10},
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50, "cache_read": 0.01},
}

FIELDS = [
    "timestamp", "run_id", "step", "model", "input_tokens", "output_tokens",
    "cache_read_input_tokens", "cache_creation_input_tokens", "cost_usd", "question",
]


def cost_usd(model: str, input_tokens: int, output_tokens: int, cache_read: int = 0,
             cache_write: int = 0) -> float:
    p = PRICES.get(model)
    if p is None:
        return float("nan")
    # zapis do cache kosztuje ok. 1.25x ceny wejścia
    total = (input_tokens * p["input"] + output_tokens * p["output"]
             + cache_read * p["cache_read"] + cache_write * p["input"] * 1.25)
    return round(total / 1_000_000, 6)


def log_usage(response, run_id: str, step: int, question: str, path=None) -> float:
    """Zapisuje usage z odpowiedzi API do CSV i zwraca koszt tego kroku w USD."""
    path = path or LOG_DIR / "usage.csv"
    u = response.usage
    cache_read = getattr(u, "cache_read_input_tokens", 0) or 0
    cache_write = getattr(u, "cache_creation_input_tokens", 0) or 0
    cost = cost_usd(response.model, u.input_tokens, u.output_tokens, cache_read, cache_write)
    path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        w.writerow({
            "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
            "run_id": run_id, "step": step, "model": response.model,
            "input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
            "cache_read_input_tokens": cache_read, "cache_creation_input_tokens": cache_write,
            "cost_usd": cost, "question": question,
        })
    return cost
