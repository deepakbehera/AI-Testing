# Exercise: Robust Code — Exceptions, Logging & Retries

**Estimated time:** 35–45 minutes

---

## Part A — Robust JSON Parser (15 min)

Create `exercises/robust_code_solution.py`.

Write a function `robust_parse_llm_response(raw: str) -> tuple[dict | None, str]` that:
1. Strips prose wrappers and markdown fences to find JSON.
2. Parses the JSON (`json.loads`).
3. Returns `(parsed_dict, "ok")` on success.
4. Returns `(None, "parse_error: <message>")` if JSON is malformed.
5. Returns `(None, "no_json_found")` if no `{...}` is present.

Catches only `json.JSONDecodeError` and `ValueError`. Does not use bare `except`.

Test it against these inputs:
```python
test_inputs = [
    '{"score": 0.87, "label": "good"}',                     # clean JSON
    'Sure! Here you go:\n```json\n{"score": 0.5}\n```',     # markdown fence
    '{"score": "not-a-number"}',                             # valid JSON, wrong type
    'No JSON here, just text',                               # no JSON
    '{"unclosed": true',                                     # malformed
]
```

---

## Part B — Logging Setup (10 min)

Add structured logging to your `robust_parse_llm_response` function:
- `log.debug` for each step (finding JSON, attempting parse)
- `log.info` on success with the number of keys found
- `log.warning` on `no_json_found`
- `log.error` on `parse_error` with the raw exception message

Configure logging at the top of your file with:
```python
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("day3")
```

Run the function on all test inputs and verify the log output makes sense.

---

## Part C — Retry Decorator (15 min)

Write a `@retry(attempts=3, base_delay=0.5)` decorator that:
1. Retries on any `Exception` (catch-all OK inside the decorator itself).
2. Uses exponential backoff with jitter.
3. Logs each retry attempt at `WARNING` level.
4. Logs the final failure at `ERROR` level before re-raising.
5. Does NOT retry on `ValueError` (pass `exceptions=(ConnectionError, TimeoutError)` instead).

Demonstrate it by decorating a `flaky_api()` function that fails 60% of the time with `ConnectionError` and succeeds 40% of the time. Run it 10 times in a loop and print how many succeeded vs. gave up.

---

## Part D — Bonus: Custom Exception (optional, +10 min)

Define:
```python
class LLMResponseError(Exception):
    def __init__(self, message: str, raw_response: str):
        super().__init__(message)
        self.raw_response = raw_response
```

Raise it from `robust_parse_llm_response` instead of returning `(None, "parse_error")`. Update callers accordingly.

---

## Self-Check

- [ ] `robust_parse_llm_response` handles all 5 test inputs correctly
- [ ] Only specific exception classes are caught — no bare `except`
- [ ] Logging output clearly distinguishes DEBUG / INFO / WARNING / ERROR
- [ ] Retry decorator logs attempt number, exception type, and delay
- [ ] You can explain why `auth` errors should NOT be retried
