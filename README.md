# F1 Data Agent

> 🚧 Work in progress

An LLM agent that answers natural-language questions about Formula 1 races.
It decides on its own which data to fetch from the [OpenF1 API](https://openf1.org),
loads it into DuckDB, writes and runs SQL, recovers from its own SQL errors,
and answers with numbers and sources. Every API call is logged with token usage and cost.

**Example:** *"Who had the fastest lap on hard tyres in the 2025 Australian GP?"*

<!-- TODO: wklej przykładowy przebieg z terminala (pytanie, wywołania narzędzi, odpowiedź, koszt) -->

## How it works

```
question ─► Claude (Messages API + tool use) ─► tool_use ─► Python executes tool ─► tool_result ─┐
               ▲                                                                                 │
               └──────────────────────────────── loop until end_turn ◄───────────────────────────┘
```

| Tool | What it does |
|---|---|
| `describe_tables` | Lists DuckDB tables with human-written descriptions, columns and row counts |
| `fetch_openf1` | Downloads an OpenF1 endpoint (allow-listed) into a DuckDB table, cached on disk |
| `run_sql` | Runs a read-only `SELECT` and returns up to 50 rows; errors go back to the model |

Design choices:
- **Hand-written agent loop** (no framework) to keep every step explicit and testable.
- **Read-only SQL + endpoint allow-list** as basic guardrails for tool calls.
- **Table descriptions as context** (same idea as semantic layers / Databricks Genie).
- **Cost tracking:** every request is logged to `logs/usage.csv` (tokens, USD).

## Evaluation

<!-- TODO (weekend 2): accuracy na N pytaniach, średni koszt i liczba kroków na pytanie -->

| Metric | Value |
|---|---|
| Questions in eval set | TODO |
| Accuracy | TODO |
| Avg. cost per question | TODO |
| Avg. tool calls per question | TODO |

## Run it

```bash
uv sync
cp .env.example .env          # add your ANTHROPIC_API_KEY
uv run python smoke_test.py   # check the API key works
uv run f1-agent "Who won the 2025 Australian Grand Prix?"
uv run pytest                 # tests run without API calls (fake client)
```

## Tech stack

Python · Anthropic Claude API (tool use) · DuckDB · pandas · OpenF1 API · pytest · GitHub Actions · uv

## What I learned

<!-- TODO: 3-5 punktów po angielsku, np. jak model naprawia błędy SQL, ile kosztuje pytanie -->
