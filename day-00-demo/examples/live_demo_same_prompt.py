"""
Live Demo 1 — Non-determinism.

Slide 12: "Same prompt, multiple runs, observe behavior."

Sends the same prompt to the same model N times and STREAMS each response
token-by-token so the class sees the LLM "thinking" live.

Default provider: Ollama running locally (no API key, no cost).
Swap to OpenAI or Anthropic by setting PROVIDER in .env.

Run:
    ollama serve                 # if not already running
    ollama pull llama3.2:3b      # one-time
    python examples/live_demo_same_prompt.py
"""

import os
import sys
import time
from typing import Iterator

from dotenv import load_dotenv

load_dotenv()

PROMPT = "Explain blockchain in simple terms."
RUNS = 5
PROVIDER = os.getenv("PROVIDER", "ollama").lower()
MODEL = os.getenv("DEMO_MODEL", "llama3.2:3b")
TEMPERATURE = 1.0
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")


def _openai_compatible_client(base_url: str | None, api_key: str):
    """Ollama, OpenAI, and LM Studio all share the same SDK surface."""
    from openai import OpenAI
    if base_url:
        return OpenAI(base_url=base_url, api_key=api_key)
    return OpenAI(api_key=api_key)


def _stream_openai_compatible(client, prompt: str) -> Iterator[str]:
    stream = client.chat.completions.create(
        model=MODEL,
        temperature=TEMPERATURE,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def stream_ollama(prompt: str) -> Iterator[str]:
    client = _openai_compatible_client(OLLAMA_BASE_URL, api_key="ollama")
    yield from _stream_openai_compatible(client, prompt)


def stream_openai(prompt: str) -> Iterator[str]:
    client = _openai_compatible_client(None, api_key=os.environ["OPENAI_API_KEY"])
    yield from _stream_openai_compatible(client, prompt)


def stream_anthropic(prompt: str) -> Iterator[str]:
    from anthropic import Anthropic
    client = Anthropic()
    with client.messages.stream(
        model=MODEL,
        max_tokens=512,
        temperature=TEMPERATURE,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            yield text


def stream_llm(prompt: str) -> Iterator[str]:
    if PROVIDER == "anthropic":
        yield from stream_anthropic(prompt)
    elif PROVIDER == "openai":
        yield from stream_openai(prompt)
    else:
        yield from stream_ollama(prompt)


def main() -> None:
    print(f"Prompt: {PROMPT!r}")
    print(f"Model:  {MODEL}  |  Provider: {PROVIDER}  |  Temperature: {TEMPERATURE}")
    print(f"Runs:   {RUNS}")
    if PROVIDER == "ollama":
        print(f"Ollama: {OLLAMA_BASE_URL}  (running locally — no API key, no cost)")
    print("=" * 72)

    lengths = []
    for i in range(1, RUNS + 1):
        print(f"\n--- Run {i} ---", flush=True)
        start = time.time()
        buffer = []
        for chunk in stream_llm(PROMPT):
            buffer.append(chunk)
            sys.stdout.write(chunk)
            sys.stdout.flush()
        elapsed = time.time() - start
        full = "".join(buffer)
        lengths.append(len(full))
        print(f"\n    ({elapsed:.1f}s, {len(full)} chars)", flush=True)

    print("\n" + "=" * 72)
    print("Observations for the class:")
    print(f"  - Response lengths: {lengths}")
    print(f"  - Shortest: {min(lengths)} chars   Longest: {max(lengths)} chars")
    print("  - Same prompt, same model — different answers every time.")
    print("  - This is why `assertEquals` doesn't work for AI output.")


if __name__ == "__main__":
    main()
