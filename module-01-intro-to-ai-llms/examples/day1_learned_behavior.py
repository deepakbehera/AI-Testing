"""
Day 1 — Attention-grabber demo (supports slides 3-6).

Point: AI is LEARNED, not programmed.

Watch a single LLM — one set of weights, no code changes, no retraining —
handle four wildly different tasks. No `if/else` could cover this.

Run:
    ollama serve
    python examples/day1_learned_behavior.py
"""

import os
import sys
from typing import Iterator
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("PROVIDER", "ollama").lower()
MODEL = os.getenv("DEMO_MODEL", "llama3.2:3b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

TASKS = [
    ("Math",
     "What is 17 squared? Answer in one line."),
    ("Creative writing",
     "Write a haiku about a flaky unit test."),
    ("Code review",
     "Spot the bug in this function:\n\n"
     "def divide(a, b):\n"
     "    return a / b\n\n"
     "Answer in two sentences."),
    ("Domain mash-up",
     "Explain microservices architecture in the style of a cooking recipe. Keep it under 80 words."),
]


def _client():
    from openai import OpenAI
    if PROVIDER == "openai":
        return OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")


def stream_llm(prompt: str) -> Iterator[str]:
    if PROVIDER == "anthropic":
        from anthropic import Anthropic
        with Anthropic().messages.stream(
            model=MODEL,
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        ) as s:
            for t in s.text_stream:
                yield t
        return
    stream = _client().chat.completions.create(
        model=MODEL,
        temperature=0.7,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def main() -> None:
    print(f"Model: {MODEL}  |  Provider: {PROVIDER}")
    print("One set of weights. Four completely different tasks.")
    print("=" * 72)

    for label, prompt in TASKS:
        print(f"\n── TASK: {label} ──")
        print(f"prompt:   {prompt.splitlines()[0]}...")
        print("response: ", end="", flush=True)
        for chunk in stream_llm(prompt):
            sys.stdout.write(chunk)
            sys.stdout.flush()
        print()

    print("\n" + "=" * 72)
    print("Same model. Zero code changes. Zero rules added.")
    print("Every output came from the same set of learned weights.")
    print("This is learned behavior, not programmed logic.")


if __name__ == "__main__":
    main()
