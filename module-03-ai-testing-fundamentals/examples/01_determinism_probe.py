"""
Day 1 — Non-determinism probe.

Calls the same prompt N times and measures how much the outputs vary.
The goal is to make non-determinism *visible and measurable*.

We use a simple token-overlap (Jaccard similarity) between response pairs.
  - Score = 1.0  →  responses are identical
  - Score = 0.0  →  responses share no tokens at all

Real-world: you'd use sentence-transformers cosine similarity for semantic
comparison. Jaccard is good enough to illustrate the concept without extra deps.

Run:
    # with Ollama (default)
    python examples/determinism_probe.py

    # with OpenAI
    PROVIDER=openai python examples/determinism_probe.py
"""

import logging
import os
import statistics
from itertools import combinations

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("determinism_probe")

# ─── configuration ────────────────────────────────────────────────────────────

PROVIDER = os.getenv("PROVIDER", "ollama").lower()
MODEL = os.getenv("DEMO_MODEL", "llama3.2:3b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
RUNS = 5

# Change this prompt to test a different task.
PROBE_PROMPT = (
    "Explain what a large language model is. "
    "Keep your answer to exactly two sentences."
)


# ─── helpers ─────────────────────────────────────────────────────────────────

def get_client() -> OpenAI:
    if PROVIDER == "openai":
        return OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")


def call_llm(client: OpenAI, prompt: str) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=TEMPERATURE,
        max_tokens=150,
    )
    return resp.choices[0].message.content.strip()


def tokenize(text: str) -> set[str]:
    """Lowercase word tokens — good enough for overlap scoring."""
    return set(text.lower().split())


def jaccard(a: str, b: str) -> float:
    """Token-level Jaccard similarity between two strings."""
    tokens_a = tokenize(a)
    tokens_b = tokenize(b)
    if not tokens_a and not tokens_b:
        return 1.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)


# ─── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    client = get_client()

    log.info("provider=%s  model=%s  temperature=%.1f  runs=%d",
             PROVIDER, MODEL, TEMPERATURE, RUNS)
    log.info("prompt: %r", PROBE_PROMPT)
    log.info("─" * 60)

    responses: list[str] = []
    for i in range(1, RUNS + 1):
        response = call_llm(client, PROBE_PROMPT)
        responses.append(response)
        log.info("run %d/%d: %s", i, RUNS, response)

    # ── pairwise Jaccard scores ──────────────────────────────────────────────
    scores: list[float] = []
    for (i, a), (j, b) in combinations(enumerate(responses, 1), 2):
        score = jaccard(a, b)
        scores.append(score)
        log.debug("jaccard(run%d, run%d) = %.3f", i, j, score)

    log.info("─" * 60)
    log.info("VARIANCE REPORT")
    log.info("  runs        : %d", RUNS)
    log.info("  temperature : %.1f", TEMPERATURE)
    log.info("  pairs scored: %d", len(scores))
    log.info("  min overlap : %.3f", min(scores))
    log.info("  max overlap : %.3f", max(scores))
    log.info("  mean overlap: %.3f", statistics.mean(scores))
    log.info("  stdev       : %.3f", statistics.stdev(scores) if len(scores) > 1 else 0.0)

    # ── interpretation ──────────────────────────────────────────────────────
    mean = statistics.mean(scores)
    if mean >= 0.85:
        verdict = "LOW variance — outputs are very consistent."
    elif mean >= 0.60:
        verdict = "MODERATE variance — outputs overlap significantly but differ in wording."
    else:
        verdict = "HIGH variance — outputs are substantially different across runs."

    log.info("  verdict     : %s", verdict)
    log.info("")
    log.info("Try me again with TEMPERATURE=0 and compare.")


if __name__ == "__main__":
    main()
