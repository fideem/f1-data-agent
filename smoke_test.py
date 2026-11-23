"""Krok 0: sprawdź, czy klucz API działa (jedno tanie zapytanie).  uv run python smoke_test.py"""

import anthropic
from dotenv import load_dotenv

from f1_agent.config import MODEL

load_dotenv()
client = anthropic.Anthropic()
response = client.messages.create(
    model=MODEL, max_tokens=200,
    messages=[{"role": "user", "content": "Powiedz 'działa' i jedno zdanie o F1."}],
)
print(next(b.text for b in response.content if b.type == "text"))
print("usage:", response.usage.input_tokens, "in /", response.usage.output_tokens, "out")
