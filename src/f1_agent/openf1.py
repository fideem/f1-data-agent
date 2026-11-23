"""Mały klient OpenF1 API z cache na dysku (gotowe).

Dlaczego cache: OpenF1 ma limity zapytań, a agent i testy często pytają o te same dane.
Każda odpowiedź jest zapisywana do data/raw/<endpoint>/<parametry>.json i przy kolejnym
wywołaniu czytana z dysku zamiast z internetu.

Używamy requests (nie pd.read_json), bo na Macu pd.read_json miał problem z SSL.
"""

import hashlib
import json
import time
from pathlib import Path

import pandas as pd
import requests

from f1_agent.config import DATA_DIR

BASE_URL = "https://api.openf1.org/v1"
RAW_DIR = DATA_DIR / "raw"

# Endpointy, z których agent może korzystać. Lista zamknięta = agent nie wymyśli
# własnego adresu URL (to też element bezpieczeństwa narzędzi).
ALLOWED_ENDPOINTS = {
    "meetings",
    "sessions",
    "drivers",
    "laps",
    "stints",
    "pit",
    "weather",
    "race_control",
    "position",
    "session_result",
}

_MIN_SECONDS_BETWEEN_CALLS = 0.4
_last_call = 0.0


def _cache_path(endpoint: str, params: dict) -> Path:
    key = json.dumps(params, sort_keys=True, default=str)
    digest = hashlib.sha1(key.encode()).hexdigest()[:16]
    return RAW_DIR / endpoint / f"{digest}.json"


def fetch(endpoint: str, use_cache: bool = True, **params) -> pd.DataFrame:
    """Pobiera dane z OpenF1 i zwraca je jako DataFrame.

    Przykład: fetch("laps", session_key=9693, driver_number=4)
    """
    global _last_call
    if endpoint not in ALLOWED_ENDPOINTS:
        raise ValueError(f"Nieznany endpoint '{endpoint}'. Dozwolone: {sorted(ALLOWED_ENDPOINTS)}")

    path = _cache_path(endpoint, params)
    if use_cache and path.exists():
        return pd.DataFrame(json.loads(path.read_text()))

    for attempt in range(4):
        wait = _MIN_SECONDS_BETWEEN_CALLS - (time.monotonic() - _last_call)
        if wait > 0:
            time.sleep(wait)
        _last_call = time.monotonic()
        resp = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=30)
        if resp.status_code == 429:  # za dużo zapytań -> odczekaj i spróbuj ponownie
            time.sleep(2 ** attempt)
            continue
        if resp.status_code == 404:  # OpenF1 zwraca 404, gdy nie ma pasujących danych
            records = []
            break
        resp.raise_for_status()
        records = resp.json()
        break
    else:
        raise RuntimeError(f"OpenF1 wciąż zwraca 429 dla {endpoint} {params}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records))
    return pd.DataFrame(records)
