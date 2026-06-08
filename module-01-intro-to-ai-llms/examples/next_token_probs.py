"""
Day 3 — Demo 3: Next Token Prediction (slide 25).

Shows the probability distribution the model produces for the next token.
This makes "LLMs don't know facts — they sample from distributions" concrete.

Requires `logprobs` support:
  - OpenAI:  works out of the box
  - Ollama:  supported on recent versions via OpenAI-compatible endpoint

If logprobs aren't returned, falls back to showing just the completion.

Run:
    # Works best with OpenAI:
    PROVIDER=openai python examples/day3_next_token_probs.py

    # Also try locally:
    ollama serve && python examples/day3_next_token_probs.py
"""

import math
import os
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("PROVIDER", "ollama").lower()
MODEL = os.getenv("DEMO_MODEL", "llama3.2:3b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

PROMPTS = [
    "The capital of France is",
    "The largest planet in our solar system is",
    "The author of Romeo and Juliet is",
    "In Python, to open a file for reading you use the function",
]


def _client():
    from openai import OpenAI
    if PROVIDER == "openai":
        return OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")


def probability_of(logprob: float) -> float:
    return math.exp(logprob)


def run_one(prompt: str) -> None:
    client = _client()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Complete the sentence with exactly one word."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=3,
        temperature=0.0,
        logprobs=True,
        top_logprobs=5,
    )

    choice = resp.choices[0]
    completion = choice.message.content.strip()
    print(f"\nPrompt: {prompt!r}")
    print(f"Completion: {completion!r}")

    logprobs_data = getattr(choice, "logprobs", None)
    if not logprobs_data or not getattr(logprobs_data, "content", None):
        print("  (no logprobs returned by this provider — "
              "try PROVIDER=openai to see the distribution)")
        return

    first_token = logprobs_data.content[0]
    print("  Top candidates for the NEXT token after the prompt:")
    for alt in first_token.top_logprobs:
        p = probability_of(alt.logprob) * 100
        print(f"    {alt.token!r:15}  {p:6.2f}%   logprob={alt.logprob:.3f}")


def main() -> None:
    print(f"Model: {MODEL}  |  Provider: {PROVIDER}")
    print("The model doesn't 'know' facts — it computes probabilities.")
    print("=" * 72)

    for p in PROMPTS:
        try:
            run_one(p)
        except Exception as exc:
            print(f"\n[error on {p!r}] {exc}")

    print("\n" + "=" * 72)
    print("Takeaway: knowledge is encoded as probability distributions,")
    print("not a factual database. The model samples; it doesn't look up.")


if __name__ == "__main__":
    main()
