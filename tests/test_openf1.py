import pytest

from f1_agent import openf1


class FakeResponse:
    status_code = 200

    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data

    def raise_for_status(self):
        pass


def test_fetch_uses_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(openf1, "RAW_DIR", tmp_path)
    calls = []

    def fake_get(url, params, timeout):
        calls.append(url)
        return FakeResponse([{"lap_number": 1, "lap_duration": 90.1}])

    monkeypatch.setattr(openf1.requests, "get", fake_get)
    df1 = openf1.fetch("laps", session_key=9693)
    df2 = openf1.fetch("laps", session_key=9693)
    assert len(calls) == 1  # drugi raz z dysku
    assert df1.equals(df2)


def test_unknown_endpoint_rejected():
    with pytest.raises(ValueError):
        openf1.fetch("hack_the_planet")
