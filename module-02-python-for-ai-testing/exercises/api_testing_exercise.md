# Exercise: API Testing with Python

**Estimated time:** 40–50 minutes

---

## Part A — Multi-Provider CLI (20 min)

Create `exercises/api_testing_solution.py` — a command-line tool to test any LLM API.

The script accepts arguments via `sys.argv` or `argparse`:
```
python api_testing_solution.py --provider ollama --model llama3.2:3b --prompt "What is RAG?"
python api_testing_solution.py --provider openai  --model gpt-4o-mini  --prompt "What is RAG?"
```

It must:
1. Load `.env` with `dotenv`.
2. Select the right client (Ollama-compat OpenAI or real OpenAI) based on `--provider`.
3. Call the model with the given prompt, `temperature=0.3`, `max_tokens=200`.
4. Print the response, latency in ms, and token usage.
5. Handle and log: `AuthenticationError` (bad key), `RateLimitError` (429), `APIConnectionError` (no server), timeout.
6. Exit with code `1` on failure, `0` on success.

---

## Part B — Normalize & Compare (15 min)

Using the `LLMResponse` dataclass from Day 4's notebook, call the **same prompt** on two providers (or two models on the same provider). Collect both responses in a list of `LLMResponse` objects.

Print a comparison table:
```
COMPARISON REPORT
=================
Prompt: "What is a context window?"

Provider   Model            Latency   Tokens  Length  Content preview
─────────────────────────────────────────────────────────────────────
ollama     llama3.2:3b      1234ms    87      312     "A context window is the max..."
openai     gpt-4o-mini      678ms     95      401     "The context window refers to..."
```

---

## Part C — Behavioral Assertion (10 min)

Write a function `assert_response_quality(resp: LLMResponse) -> tuple[bool, list[str]]` that checks:

| Rule | Threshold |
|---|---|
| Not empty | `len(content) > 0` |
| Not too long | `< 2000 chars` |
| Not a refusal | None of the refusal signals present |
| Latency | `< 10000ms` |
| Token efficiency | `output_tokens / prompt_tokens >= 0.5` (model must generate at least half as many tokens as it received) |

Run it on both responses from Part B and print PASS/FAIL per check.

---

## Part D — Bonus: HTTP Headers Inspector (optional, +10 min)

Use `requests` directly (not the SDK) to call `https://api.openai.com/v1/chat/completions`. Inspect the response headers to find:
- `x-ratelimit-remaining-requests` — how many requests left before hitting the rate limit
- `x-ratelimit-reset-requests` — when the rate limit resets
- `openai-processing-ms` — actual server processing time (vs. your measured latency)

Print these alongside the response.

---

## Self-Check

- [ ] CLI script runs with `--provider ollama` without errors
- [ ] `AuthenticationError` produces a clear, actionable error message (not a stack trace)
- [ ] `LLMResponse` dataclass has all required fields
- [ ] Comparison table shows both providers side-by-side
- [ ] `assert_response_quality` catches an empty response as a failure
- [ ] Exit codes are correct (0 = success, 1 = failure)
