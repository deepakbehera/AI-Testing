"""
Day 3 — Demo 5: Context Retention / Window (slide 29).

We plant an important fact ("My name is Rahul") at the start, pad the
conversation with filler until we OVERFLOW the context window, then ask
the model to recall the name.

For llama3.2:3b the default context is 4096 tokens — plenty for anything
normal. To make truncation visible in a live demo we squeeze the context
down to 512 tokens via Ollama's `num_ctx` option, so a few filler turns
push the original fact out.

Two passes for comparison:
  Pass 1 — small window (num_ctx=512):   model LOSES the name.
  Pass 2 — normal window (num_ctx=4096): model RECALLS the name.

Run:
    ollama serve
    python examples/day3_context_window.py
"""

import os
import sys
from typing import Iterator
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("PROVIDER", "ollama").lower()
MODEL = os.getenv("DEMO_MODEL", "llama3.2:3b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

if PROVIDER != "ollama":
    print("This demo uses Ollama's `num_ctx` to shrink the context window.")
    print("Set PROVIDER=ollama in .env and rerun.")
    raise SystemExit(1)


FACT_TURN = "My name is Rahul. Please remember this for the rest of our conversation."

# Filler that eats tokens without saying anything meaningful.
FILLER_TURNS = [
    "Tell me three interesting facts about octopuses in detail.",
    "Explain the rules of cricket to a complete beginner, step by step.",
    "Describe what happens during the water cycle, with examples.",
    "List the planets in our solar system and one fact about each.",
    "Summarize the plot of a classic fairy tale of your choice.",
]

RECALL_QUESTION = "What is my name? Answer with just the name."


def _client():
    from openai import OpenAI
    return OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")


def chat_stream(messages: list[dict], num_ctx: int) -> Iterator[str]:
    """Stream a chat completion with a forced context size (Ollama only)."""
    stream = _client().chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.3,
        stream=True,
        # Ollama passes extra options through `extra_body`.
        extra_body={"options": {"num_ctx": num_ctx}},
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def run_conversation(num_ctx: int, label: str) -> str:
    print(f"\n═══ Pass: {label}  (num_ctx={num_ctx}) ═══")

    messages = []

    # Turn 1: plant the fact
    print(f"\n[turn 1] user: {FACT_TURN}")
    messages.append({"role": "user", "content": FACT_TURN})
    print("[turn 1] assistant: ", end="", flush=True)
    reply_buf = []
    for chunk in chat_stream(messages, num_ctx):
        sys.stdout.write(chunk); sys.stdout.flush()
        reply_buf.append(chunk)
    print()
    messages.append({"role": "assistant", "content": "".join(reply_buf)})

    # Turns 2..N: filler to consume tokens
    for i, filler in enumerate(FILLER_TURNS, start=2):
        print(f"\n[turn {i}] user: {filler}")
        messages.append({"role": "user", "content": filler})
        print(f"[turn {i}] assistant: ", end="", flush=True)
        reply_buf = []
        for chunk in chat_stream(messages, num_ctx):
            sys.stdout.write(chunk); sys.stdout.flush()
            reply_buf.append(chunk)
        print()
        messages.append({"role": "assistant", "content": "".join(reply_buf)})

    # Final turn: ask for the name
    print(f"\n[turn {len(FILLER_TURNS) + 2}] user: {RECALL_QUESTION}")
    messages.append({"role": "user", "content": RECALL_QUESTION})
    print(f"[turn {len(FILLER_TURNS) + 2}] assistant: ", end="", flush=True)
    final_buf = []
    for chunk in chat_stream(messages, num_ctx):
        sys.stdout.write(chunk); sys.stdout.flush()
        final_buf.append(chunk)
    print()
    return "".join(final_buf).strip()


def main() -> None:
    print(f"Model: {MODEL}  |  Provider: {PROVIDER}")
    print("We plant a fact, bury it in filler, then ask the model to recall it.")
    print("=" * 72)

    small = run_conversation(num_ctx=512, label="tight window")
    large = run_conversation(num_ctx=4096, label="normal window")

    print("\n" + "=" * 72)
    print("Recall with tight window (512):  ", repr(small))
    print("Recall with normal window (4096):", repr(large))
    print()
    print("When context overflows, the oldest tokens fall out of the window.")
    print("The model didn't forget — the fact was never in front of it.")


if __name__ == "__main__":
    main()
