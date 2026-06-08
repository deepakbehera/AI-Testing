"""
Day 3 — Demo 4: Temperature Effect (slide 27).

Low temperature → sharp distribution → repeated, safe outputs.
High temperature → flat distribution → diverse, creative outputs.

Runs the same prompt three times at temperature=0.2, then three at 1.2,
so students can see the spread collapse and expand.

Run:
    ollama serve
    python examples/day3_temperature_effect.py
"""

import os
import sys
from typing import Iterator
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("PROVIDER", "ollama").lower()
MODEL = os.getenv("DEMO_MODEL", "llama3.2:3b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

PROMPT = "Write a one-line tagline for a new coffee brand. No hashtags."
RUNS = 3
TEMPERATURES = [0.2, 1.2]


def _client():
    from openai import OpenAI
    if PROVIDER == "openai":
        return OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")


def stream_llm(prompt: str, temperature: float) -> Iterator[str]:
    if PROVIDER == "anthropic":
        from anthropic import Anthropic
        with Anthropic().messages.stream(
            model=MODEL,
            max_tokens=80,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        ) as s:
            for t in s.text_stream:
                yield t
        return
    stream = _client().chat.completions.create(
        model=MODEL,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def main() -> None:
    print(f"Model: {MODEL}  |  Provider: {PROVIDER}")
    print(f"Prompt: {PROMPT!r}")
    print(f"Runs per temperature: {RUNS}")
    print("=" * 72)

    for temp in TEMPERATURES:
        label = "LOW" if temp < 0.5 else "HIGH"
        print(f"\n─── Temperature {temp}  ({label}) ───")
        for i in range(1, RUNS + 1):
            print(f"Run {i}: ", end="", flush=True)
            for chunk in stream_llm(PROMPT, temp):
                sys.stdout.write(chunk)
                sys.stdout.flush()
            print()

    print("\n" + "=" * 72)
    print("Observations:")
    print("  - At 0.2: outputs cluster — the model picks the safe, dominant token.")
    print("  - At 1.2: outputs spread — lower-probability tokens get sampled.")
    print("  - Same model. Same prompt. The knob in the middle changes EVERYTHING.")


if __name__ == "__main__":
    main()
