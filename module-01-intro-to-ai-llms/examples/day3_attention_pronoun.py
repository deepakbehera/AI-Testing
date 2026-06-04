"""
Day 3 — Demo 2: Attention in Action (slide 22).

Classic Winograd-style pair. The pronoun "it" refers to different things
depending on whether the adjective is "big" or "small". Self-attention
lets the transformer dynamically resolve this.

Run:
    ollama serve
    python examples/day3_attention_pronoun.py
"""

import os
import sys
from typing import Iterator
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("PROVIDER", "ollama").lower()
MODEL = os.getenv("DEMO_MODEL", "llama3.2:3b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

PROMPT_BIG = (
    "The trophy didn't fit in the suitcase because it was too big. "
    "In this sentence, what does 'it' refer to, and why? Answer in 2 sentences."
)
PROMPT_SMALL = (
    "The trophy didn't fit in the suitcase because it was too small. "
    "In this sentence, what does 'it' refer to, and why? Answer in 2 sentences."
)


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
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        ) as s:
            for t in s.text_stream:
                yield t
        return
    stream = _client().chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def main() -> None:
    print(f"Model: {MODEL}  |  Provider: {PROVIDER}")
    print("Same pronoun 'it'. Different adjective. Watch the reasoning flip.")
    print("=" * 72)

    for label, prompt in [("BIG", PROMPT_BIG), ("SMALL", PROMPT_SMALL)]:
        print(f"\n--- Variant: ...too {label} ---")
        print(f"prompt:   {prompt}")
        print("response: ", end="", flush=True)
        for chunk in stream_llm(prompt):
            sys.stdout.write(chunk)
            sys.stdout.flush()
        print()

    print("\n" + "=" * 72)
    print("Observations:")
    print("  - One-word change flips the referent of 'it'.")
    print("  - Self-attention lets every token weigh every other token.")
    print("  - The model doesn't read left-to-right — it reads all-to-all.")


if __name__ == "__main__":
    main()
