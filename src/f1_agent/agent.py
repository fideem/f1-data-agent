"""Pętla agenta: serce projektu. Tę część piszesz sama (na rozmowie zapytają właśnie o nią).

Piszemy pętlę ręcznie (zamiast gotowego tool_runnera z SDK), żeby rozumieć każdy krok.
Dokumentacja: https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview

Schemat jednej odpowiedzi na pytanie:

    messages = [pytanie użytkownika]
    powtarzaj (max MAX_STEPS razy):
        response = client.messages.create(model, system, tools, messages)
        zaloguj koszt
        jeśli response.stop_reason == "end_turn":  -> model skończył, zwróć tekst
        jeśli == "tool_use":
            dopisz odpowiedź modelu do messages (rola "assistant", CAŁE response.content)
            dla każdego bloku typu "tool_use": wykonaj narzędzie
            dopisz WSZYSTKIE wyniki w JEDNEJ wiadomości (rola "user") jako bloki tool_result
    jeśli skończyły się kroki -> zwróć komunikat, że agent nie zdążył
"""

import uuid
from dataclasses import dataclass, field

import anthropic

from f1_agent import config, db
from f1_agent.cost import log_usage
from f1_agent.prompts import SYSTEM_PROMPT
from f1_agent.tools import TOOLS, execute_tool


@dataclass
class AgentResult:
    answer: str
    steps: int
    cost_usd: float
    tool_calls: list[dict] = field(default_factory=list)  # [{"name":..., "input":..., "is_error":...}]


def run_agent(question: str, client: anthropic.Anthropic | None = None, con=None,
              verbose: bool = True) -> AgentResult:
    client = client or anthropic.Anthropic()  # klucz czyta sam z ANTHROPIC_API_KEY (.env)
    con = con or db.connect()
    run_id = uuid.uuid4().hex[:8]
    messages = [{"role": "user", "content": question}]
    tool_calls: list[dict] = []
    total_cost = 0.0

    for step in range(1, config.MAX_STEPS + 1):
        # TODO A: wywołaj model.
        #   response = client.messages.create(
        #       model=config.MODEL, max_tokens=config.MAX_TOKENS,
        #       system=SYSTEM_PROMPT, tools=TOOLS, messages=messages)
        # TODO B: total_cost += log_usage(response, run_id, step, question)
        # TODO C: jeśli response.stop_reason == "end_turn": zbierz tekst ze wszystkich
        #   bloków, gdzie block.type == "text", i zwróć AgentResult(...).
        # TODO D: inaczej (stop_reason == "tool_use"):
        #   - messages.append({"role": "assistant", "content": response.content})
        #   - dla każdego block w response.content z block.type == "tool_use":
        #         text, is_error = execute_tool(con, block.name, block.input)
        #         dodaj {"type": "tool_result", "tool_use_id": block.id,
        #                "content": text, "is_error": is_error} do listy wyników
        #         dopisz {"name": block.name, "input": block.input, "is_error": is_error}
        #         do tool_calls (przyda się w ewaluacji!)
        #         jeśli verbose: wypisz, jakie narzędzie i z jakimi argumentami
        #   - messages.append({"role": "user", "content": lista_wyników})
        # Pytanie kontrolne: dlaczego wyniki wszystkich narzędzi idą w JEDNEJ wiadomości?
        raise NotImplementedError("TODO A-D: pętla agenta")

    return AgentResult(
        answer=f"Nie udało się odpowiedzieć w {config.MAX_STEPS} krokach.",
        steps=config.MAX_STEPS, cost_usd=total_cost, tool_calls=tool_calls,
    )
