import math
from types import SimpleNamespace

from f1_agent.cost import cost_usd, log_usage


def test_cost_for_known_model():
    # 1 mln tokenów wejścia Opus 5.5 = $4, 1 mln wyjścia = $20
    assert cost_usd("claude-opus-5-5", 1_000_000, 0) == 4.0
    assert cost_usd("claude-opus-5-5", 0, 1_000_000) == 20.0


def test_unknown_model_gives_nan():
    assert math.isnan(cost_usd("model-ktorego-nie-ma", 10, 10))


def test_log_usage_appends_rows(tmp_path):
    usage = SimpleNamespace(input_tokens=1000, output_tokens=200,
                            cache_read_input_tokens=0, cache_creation_input_tokens=0)
    response = SimpleNamespace(model="claude-opus-5-5", usage=usage)
    path = tmp_path / "usage.csv"
    log_usage(response, "run1", 1, "pytanie", path=path)
    log_usage(response, "run1", 2, "pytanie", path=path)
    lines = path.read_text().strip().splitlines()
    assert len(lines) == 3  # nagłówek + 2 wiersze
