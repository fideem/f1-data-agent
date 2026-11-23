"""Konfiguracja wczytywana z pliku .env (gotowe, nie musisz tu nic zmieniać)."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
DB_PATH = DATA_DIR / "f1.duckdb"

MODEL = os.getenv("F1_AGENT_MODEL", "claude-opus-5-5")
MAX_STEPS = int(os.getenv("F1_AGENT_MAX_STEPS", "8"))
MAX_TOKENS = 16000
