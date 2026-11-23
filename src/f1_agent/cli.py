"""Uruchamianie z terminala (gotowe):  uv run f1-agent "Kto wygrał GP Australii 2025?" """

import sys

from f1_agent.agent import run_agent


def main() -> None:
    if len(sys.argv) < 2:
        print('Użycie: uv run f1-agent "twoje pytanie o F1"')
        sys.exit(1)
    result = run_agent(" ".join(sys.argv[1:]))
    print("\n" + result.answer)
    print(f"\n[{result.steps} kroków, {len(result.tool_calls)} wywołań narzędzi, "
          f"koszt ${result.cost_usd:.4f}]")


if __name__ == "__main__":
    main()
