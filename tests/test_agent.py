"""Test pętli agenta BEZ prawdziwego API (fałszywy klient). Dzięki temu CI na GitHubie
nie potrzebuje klucza i nic nie kosztuje. Przejdzie, gdy zrobisz TODO A-D w agent.py."""

from types import SimpleNamespace

from f1_agent import agent


def _usage():
    return SimpleNamespace(input_tokens=100, output_tokens=20,
                           cache_read_input_tokens=0, cache_creation_input_tokens=0)


class FakeMessages:
    def __init__(self):
        self.calls = 0

    def create(self, **kwargs):
        self.calls += 1
        if self.calls == 1:  # najpierw model prosi o narzędzie
            block = SimpleNamespace(type="tool_use", id="toolu_1", name="describe_tables", input={})
            return SimpleNamespace(stop_reason="tool_use", content=[block],
                                   model="claude-opus-5-5", usage=_usage())
        # potem sprawdzamy, że dostał wynik narzędzia, i kończy
        last = kwargs["messages"][-1]
        assert last["role"] == "user"
        assert last["content"][0]["type"] == "tool_result"
        assert last["content"][0]["tool_use_id"] == "toolu_1"
        text = SimpleNamespace(type="text", text="Najszybsze okrążenie: 89.1 s")
        return SimpleNamespace(stop_reason="end_turn", content=[text],
                               model="claude-opus-5-5", usage=_usage())


def test_agent_loop_with_fake_client(con_with_laps, tmp_path, monkeypatch):
    monkeypatch.setattr(agent, "log_usage", lambda *a, **k: 0.001)
    client = SimpleNamespace(messages=FakeMessages())
    result = agent.run_agent("Najszybsze okrążenie?", client=client, con=con_with_laps,
                             verbose=False)
    assert "89.1" in result.answer
    assert result.steps == 2
    assert [c["name"] for c in result.tool_calls] == ["describe_tables"]
