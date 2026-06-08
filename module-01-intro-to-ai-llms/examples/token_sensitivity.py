"""
Day 2 — Demo 1: Token Sensitivity (slide 17).

Same meaning, different wording → different tokens → different embeddings
→ different output.

We show tokens for both prompts (via tiktoken) so students SEE the
difference, then stream both responses side by side.

Run:
    ollama serve
    python examples/day2_token_sensitivity.py
"""

import os
import sys
from typing import Iterator
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("PROVIDER", "ollama").lower()
MODEL = os.getenv("DEMO_MODEL", "llama3.2:3b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

PROMPT_A = "Explain Artificial Intelligence in simple terms."
PROMPT_B = "Explain AI simply."


def show_tokens(label: str, text: str) -> None:
    """Visualise how a tokenizer breaks up the prompt."""
    try:
        import tiktoken
    except ImportError:
        print(f"[Prompt {label}] tiktoken not installed — skipping token view")
        print(f"         Install: pip install tiktoken")
        return
    enc = tiktoken.get_encoding("cl100k_base")   # GPT-style BPE
    ids = enc.encode(text)
    tokens = [enc.decode([i]) for i in ids]
    print(f"[Prompt {label}] {text!r}")
    print(f"            tokens ({len(ids)}): {tokens}")
    print(f"            ids:              {ids}")


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
    print("Same question. Different phrasing. Watch what happens.")
    print("=" * 72)

    print("\n--- Tokenization view ---")
    show_tokens("A", PROMPT_A)
    show_tokens("B", PROMPT_B)

    for label, prompt in [("A", PROMPT_A), ("B", PROMPT_B)]:
        print(f"\n--- Response to Prompt {label} ---")
        print(f"prompt:   {prompt}")
        print("response: ", end="", flush=True)
        for chunk in stream_llm(prompt):
            sys.stdout.write(chunk)
            sys.stdout.flush()
        print()

    print("\n" + "=" * 72)
    print("Observations:")
    print("  - Prompt A and Prompt B mean the same thing to a human.")
    print("  - To the model they're different token sequences.")
    print("  - Different tokens → different embeddings → different outputs.")
    print("  - This is why prompt wording is part of your test surface.")


if __name__ == "__main__":
    main()
