# Module 2 — Python for AI Testing & Automation

**Duration:** 7 hours · split across **7 online sessions of 1 hour each**
**Prerequisites:** Module 1 (concepts only — no coding required). A laptop with macOS / Linux / Windows and internet.

This module is where Module 1's ideas become a working toolkit. By the end of Day 7 you will have a real Python test framework that calls LLMs, validates responses, and runs automatically on every push to GitHub.

---

## How the 7 sessions are organized

| Day | Focus | What you'll build |
|---|---|---|
| **1** | Python setup, venv, syntax basics | A running Python environment + prompt classifier |
| **2** | Data structures — lists, dicts, JSON | A script that parses & validates LLM responses |
| **3** | Robust code — exceptions, logging, retries | An LLM client that survives failures |
| **4** | API testing — `requests`, `.env`, 3 providers | A CLI that tests any LLM API |
| **5** | `pytest` — first tests, fixtures, parametrize | A pytest suite hitting a real LLM |
| **6** | Test framework structure, golden data, reports | A reusable mini framework |
| **7** | GitHub Actions — CI, secrets, artifacts | A green CI pipeline |

Each day has a notebook in [`examples/`](examples/) and an exercise in [`exercises/`](exercises/). Do the exercises between sessions — 30–40 min each. They compound.

---

## DAY 1 — Python Setup & Syntax (60 min)

### Learning objectives
- Install Python 3.10+ and verify it works
- Create and activate a virtual environment
- Read and write all basic Python: variables, types, strings, loops, functions, comprehensions
- Build a capstone prompt classifier using dataclasses

### Key concepts

**Python version.** We use Python 3.10+. If `python --version` shows `2.x`, use `python3`. They are different languages in practice.

**Virtual environment (`venv`).** An isolated Python setup so one project's libraries don't collide with another's.

> **Plain English:** a venv is a separate kitchen for each recipe. Salt from last night's pasta doesn't end up in tomorrow's dessert. Same with Python packages.

**Types you'll use constantly.**

| Type | Example | Notes |
|---|---|---|
| `str` | `"hello"` | Text — immutable |
| `int` | `42` | Whole number |
| `float` | `0.95` | Decimal |
| `bool` | `True` / `False` | Capitalized |
| `list` | `[1, 2, 3]` | Ordered, mutable |
| `dict` | `{"k": "v"}` | Key-value, mutable |
| `None` | `None` | Absence of value |

**Type checking.** Use `isinstance(x, str)` — never `type(x) == str`. `isinstance` handles subclasses correctly.

**Type conversion.** `int("42")` → `42`, `str(3.14)` → `"3.14"`, `float("1.5")` → `1.5`. Wrap in `try/except ValueError` when the input comes from outside.

**String methods you'll use every day.**

```python
s = "  Hello, World!  "
s.strip()          # "Hello, World!"
s.lower()          # "  hello, world!  "
s.split(", ")      # ["  Hello", "World!  "]
", ".join(["a","b","c"])  # "a, b, c"
s[2:7]             # "Hello" (slicing — works on any sequence)
f"Score: {0.87:.2f}"     # "Score: 0.87" (f-strings)
```

**Regex basics.** `re.findall(pattern, text)` and `re.sub(pattern, replacement, text)` cover 90% of needs. For LLM output: strip markdown fences, extract JSON blocks, find code snippets.

**Conditionals — full grammar.**

```python
# ternary
label = "pass" if score >= 0.7 else "fail"

# truthiness: "", 0, [], {}, None are all falsy
if response:        # True if non-empty string

# chained comparison
if 0.5 <= score <= 1.0:
    ...

# membership
if "berlin" in response.lower():
    ...
```

**Functions — full grammar.**

```python
def classify(text: str, threshold: float = 0.7) -> dict:
    ...

def multi_call(*args, **kwargs):  # any number of positional / keyword args
    ...

def split_result() -> tuple[bool, str]:
    return True, "ok"            # multiple return values

passed, reason = split_result()  # unpack
```

**List & dict comprehensions.**

```python
scores = [0.9, 0.4, 0.8, 0.3]
passing = [s for s in scores if s >= 0.7]          # filter
labels  = {k: v.upper() for k, v in d.items()}     # dict comp
```

**Essential built-ins for AI testing.**

```python
any(kw in response for kw in keywords)   # at least one match
all(kw in response for kw in keywords)   # all must match
sorted(results, key=lambda r: r.latency) # sort by field
list(map(str.strip, raw_list))           # apply function
list(filter(None, maybe_empty_list))     # remove falsy
list(zip(prompts, responses))            # pair two lists
```

**`if __name__ == "__main__"` guard.** Prevents demo code from running when a file is imported as a module. Always use it in runnable scripts.

**`@dataclass`.** A decorator that auto-generates `__init__`, `__repr__`, `__eq__` from annotated fields. Ideal for structured results:

```python
from dataclasses import dataclass, field

@dataclass
class PromptCheck:
    category: str
    passed: bool
    score: float
    reasons: list[str] = field(default_factory=list)
```

### Capstone — prompt classifier
The Day 1 notebook ends with a full `classify_prompt(text) -> PromptCheck` function that detects category (question / instruction / harmful / other), scores confidence, and returns a `PromptCheck` dataclass.

### Try it yourself
```bash
cd module-02-python-for-ai-testing
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook examples/python_quickstart.ipynb
```

Exercise: [`exercises/python_setup_exercise.md`](exercises/python_setup_exercise.md)

---

## DAY 2 — Data Structures & JSON (60 min)

### Learning objectives
- Use lists and dicts confidently — all methods, not just the basics
- Navigate deeply nested structures (OpenAI vs Anthropic response shapes)
- Parse, validate, and write JSON
- Build a golden dataset and an evaluator

### Key concepts

**Lists — full toolkit.**

```python
models = ["claude", "gpt-4", "llama"]
models.append("gemini")          # add to end
models.insert(1, "mistral")      # add at index
models.extend(["phi", "qwen"])   # merge another list
models.remove("llama")           # remove by value (first match)
models.pop(0)                    # remove & return by index
models.index("gpt-4")            # find index (raises if not found)
models.count("gpt-4")            # how many occurrences

# slicing
models[1:3]   # index 1 up to (not including) 3
models[-2:]   # last two
models[::-1]  # reversed copy

# flatten nested
import itertools
flat = list(itertools.chain.from_iterable(nested_list))
```

**Dicts — full toolkit.**

```python
cfg = {"model": "gpt-4o-mini", "temp": 0.7}
cfg.get("max_tokens", 200)        # safe access with default
cfg.setdefault("stream", False)   # set only if key absent
cfg | {"timeout": 30}             # merge (Python 3.9+, non-destructive)

from collections import defaultdict
grouped = defaultdict(list)
for item in items:
    grouped[item["category"]].append(item)

# iterate
for key, value in cfg.items(): ...
list(cfg.keys())   # keys view as list
list(cfg.values()) # values view as list
```

**Navigating nested structures.** OpenAI and Anthropic return different shapes for the same thing:

```python
# OpenAI
text = response.choices[0].message.content

# Anthropic
text = response.content[0].text

# Safe extraction with fallback
def extract_text(response, provider: str) -> str:
    if provider == "openai":
        return response.choices[0].message.content or ""
    elif provider == "anthropic":
        return response.content[0].text if response.content else ""
    raise ValueError(f"Unknown provider: {provider}")
```

**JSON — complete grammar.**

```python
import json

# parse
data = json.loads('{"score": 0.9}')

# serialize
text = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False)

# file I/O
from pathlib import Path
data = json.loads(Path("golden.json").read_text())
Path("output.json").write_text(json.dumps(data, indent=2))
```

**`safe_parse()` — LLM output reality.** LLMs don't return clean JSON. They wrap it in markdown fences, add prose before/after. `safe_parse()` strips fences with regex, then extracts the first `{...}` block:

```python
import re, json

def safe_parse(raw: str) -> dict | None:
    text = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`")
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None
```

**Golden dataset format.**

```json
{
  "id": "capitals-001",
  "prompt": "What is the capital of France?",
  "must_include": ["paris"],
  "must_not_include": ["london", "berlin"],
  "min_length": 5,
  "max_length": 500,
  "expects_refusal": false
}
```

**Evaluating a case:**

```python
def evaluate_case(case: dict, response: str) -> tuple[bool, list[str]]:
    failures = []
    text = response.lower()
    for kw in case.get("must_include", []):
        if kw.lower() not in text:
            failures.append(f"missing keyword: {kw!r}")
    for kw in case.get("must_not_include", []):
        if kw.lower() in text:
            failures.append(f"forbidden keyword: {kw!r}")
    length = len(response)
    if length < case.get("min_length", 0):
        failures.append(f"too short: {length} < {case['min_length']}")
    if length > case.get("max_length", 99999):
        failures.append(f"too long: {length} > {case['max_length']}")
    return len(failures) == 0, failures
```

Exercise: [`exercises/data_structures_json_exercise.md`](exercises/data_structures_json_exercise.md)

---

## DAY 3 — Robust Code: Exceptions, Logging, Retries (60 min)

### Learning objectives
- Write try/except/else/finally with correct exception targeting
- Use the Python logging module at all five levels
- Build a retry decorator with exponential backoff + jitter
- Know which exceptions should NOT be retried

### Key concepts

**Full exception grammar.**

```python
try:
    result = call_api()
except json.JSONDecodeError as e:
    log.error("Bad JSON: %s", e)
except (ConnectionError, TimeoutError) as e:
    log.warning("Network error: %s", e)
    raise                      # re-raise after logging
else:
    log.info("Success: %d keys", len(result))  # runs only if no exception
finally:
    log.debug("Attempt complete")              # always runs
```

**Never use bare `except:`.** It catches `SystemExit`, `KeyboardInterrupt`, and hides real bugs. Always name the exception class.

**Exception hierarchy (relevant subset):**

```
BaseException
├── KeyboardInterrupt     ← never catch this
├── SystemExit            ← never catch this
└── Exception
    ├── ValueError        ← bad input — don't retry
    ├── TypeError         ← wrong type — don't retry
    ├── OSError
    │   ├── ConnectionError    ← retry OK
    │   └── TimeoutError       ← retry OK
    └── json.JSONDecodeError   ← don't retry
```

**Logging — all five levels.**

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("mymodule")

log.debug("Attempting parse on %d chars", len(raw))   # dev detail
log.info("Parsed %d keys successfully", len(result))  # normal ops
log.warning("No JSON found in response")              # degraded but alive
log.error("Parse failed: %s", e)                      # something broke
log.critical("Config missing — cannot start")         # fatal
log.exception("Unexpected error")                     # error + full traceback
```

> **`log.exception()`** is the same as `log.error()` but automatically appends the current exception traceback. Use it inside `except` blocks.

**Why logging beats print:**

| | `print` | `logging` |
|---|---|---|
| Levels | None | 5 levels |
| Format | Raw | Timestamped, named |
| Output target | stdout only | File, stream, remote |
| Toggle off | Delete the line | Change log level |
| Production use | No | Yes |

**Retry decorator with exponential backoff + jitter.**

```python
import time, random, functools, logging

def retry(attempts=3, base_delay=1.0, exceptions=(Exception,)):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    if attempt == attempts:
                        log.error("All %d attempts failed: %s", attempts, e)
                        raise
                    delay = base_delay * (2 ** (attempt - 1)) + random.random()
                    log.warning("Attempt %d/%d failed (%s). Retrying in %.1fs",
                                attempt, attempts, type(e).__name__, delay)
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(attempts=3, base_delay=0.5, exceptions=(ConnectionError, TimeoutError))
def call_api(prompt: str) -> str:
    ...
```

**Which errors should NOT be retried:**
- `AuthenticationError` — bad key; retrying won't fix it
- `ValueError` — your code is wrong; retrying won't fix it
- `json.JSONDecodeError` — bad response shape; retry may just produce the same bad output

Exercise: [`exercises/robust_code_exercise.md`](exercises/robust_code_exercise.md)

---

## DAY 4 — API Testing with Python (60 min)

### Learning objectives
- Use `requests` for raw HTTP calls
- Use the OpenAI and Anthropic SDKs (including streaming and multi-turn)
- Load secrets safely from `.env` — never hard-code keys
- Build a normalized `LLMResponse` dataclass and an `LLMClient` class
- Write a behavioral assertion function

### Key concepts

**HTTP status codes you must know.**

| Code | Meaning | Who's fault |
|---|---|---|
| 200 | OK | — |
| 400 | Bad Request | Your payload is malformed |
| 401 | Unauthorized | Missing / invalid API key |
| 403 | Forbidden | Key valid, but no permission |
| 422 | Unprocessable Entity | Valid JSON, invalid params |
| 429 | Rate Limited | You're calling too fast |
| 500 | Internal Server Error | Their problem |
| 503 | Service Unavailable | Their problem (retry later) |

**`requests` patterns.**

```python
import requests

# GET
resp = requests.get(url, headers={"Authorization": f"Bearer {key}"}, timeout=10)
resp.raise_for_status()   # raises HTTPError for 4xx/5xx
data = resp.json()

# POST with body
resp = requests.post(url, json=payload, headers=headers, timeout=30)

# specific exception handling
try:
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
except requests.exceptions.ConnectionError:
    ...  # network unreachable
except requests.exceptions.Timeout:
    ...  # server too slow
except requests.exceptions.HTTPError as e:
    ...  # 4xx / 5xx
```

**`.env` + `python-dotenv` — the right pattern.**

```python
from dotenv import load_dotenv
import os

load_dotenv()   # reads .env into os.environ

def require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Required env var {key!r} is not set. Check your .env file.")
    return value

api_key = require_env("OPENAI_API_KEY")

# Always mask keys in logs
log.info("Using key: %s...%s", api_key[:4], api_key[-4:])
```

**OpenAI SDK — basic, multi-turn, streaming.**

```python
from openai import OpenAI
client = OpenAI()

# basic
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What is RAG?"}],
    temperature=0.3,
    max_tokens=300,
)
text = resp.choices[0].message.content

# multi-turn: just keep appending to messages list
messages = [{"role": "system", "content": "You are a helpful assistant."}]
messages.append({"role": "user", "content": "What is embedding?"})
resp = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
messages.append({"role": "assistant", "content": resp.choices[0].message.content})

# streaming
for chunk in client.chat.completions.create(..., stream=True):
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

**Anthropic SDK — key differences.**

```python
from anthropic import Anthropic
client = Anthropic()

resp = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=300,
    system="You are a helpful assistant.",  # system is a top-level param, not a message
    messages=[{"role": "user", "content": "What is RAG?"}],
)
text = resp.content[0].text   # content is a list, not a single string
tokens_used = resp.usage.input_tokens + resp.usage.output_tokens
```

**`LLMResponse` dataclass — normalize across providers.**

```python
from dataclasses import dataclass

@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    finish_reason: str

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens
```

**Behavioral assertion function.**

```python
REFUSAL_SIGNALS = ["i can't", "i cannot", "i'm unable", "as an ai"]

def assert_response(resp: LLMResponse,
                    must_include: list[str] | None = None,
                    must_not_include: list[str] | None = None,
                    max_latency_ms: float = 10_000) -> tuple[bool, list[str]]:
    failures = []
    if not resp.content:
        failures.append("empty response")
    for kw in (must_include or []):
        if kw.lower() not in resp.content.lower():
            failures.append(f"missing: {kw!r}")
    for kw in (must_not_include or []):
        if kw.lower() in resp.content.lower():
            failures.append(f"forbidden: {kw!r}")
    if resp.latency_ms > max_latency_ms:
        failures.append(f"too slow: {resp.latency_ms:.0f}ms > {max_latency_ms}ms")
    return len(failures) == 0, failures
```

Exercise: [`exercises/api_testing_exercise.md`](exercises/api_testing_exercise.md)

---

## DAY 5 — Introduction to pytest (60 min)

### Learning objectives
- Write `test_*.py` files with correct pytest conventions
- Use `assert` with meaningful failure output
- Create function- and session-scoped fixtures
- Use `yield` fixtures for teardown
- Parametrize tests with `@pytest.mark.parametrize` and `pytest.param`
- Use built-in and custom markers: `skip`, `skipif`, `xfail`, custom
- Run tests in notebooks via `%%writefile` + `!pytest`

### Key concepts

**pytest finds tests by convention.** Files named `test_*.py` or `*_test.py`. Functions named `test_*`. Classes named `Test*`. No imports needed from pytest for basic usage.

**`assert` shows both sides on failure.** Unlike `unittest`, pytest introspects assertions:

```python
assert response == "Paris"
# AssertionError: assert 'Paris, France' == 'Paris'
```

**Fixtures — setup code that tests can request by name.**

```python
import pytest

@pytest.fixture
def sample_response():
    return {"content": "Paris", "latency_ms": 234}

def test_has_content(sample_response):    # pytest injects the fixture
    assert sample_response["content"]
```

**`yield` fixtures for teardown.**

```python
@pytest.fixture
def temp_file(tmp_path):           # tmp_path is a built-in fixture
    path = tmp_path / "test.json"
    path.write_text('{"k": "v"}')
    yield path                     # test runs here
    path.unlink(missing_ok=True)   # teardown after test
```

**Fixture scopes — how long the fixture lives.**

| Scope | Created once per... | Use for |
|---|---|---|
| `function` (default) | Test function | Anything that must be fresh |
| `class` | Test class | Shared class setup |
| `module` | `.py` file | Moderate cost setup |
| `session` | Entire test run | Expensive things: DB connection, LLM client |

```python
@pytest.fixture(scope="session")
def llm_client():
    return OpenAI()   # one client for all tests in the run
```

**`@pytest.mark.parametrize` — one function, many inputs.**

```python
@pytest.mark.parametrize("country, capital", [
    ("France", "paris"),
    ("Germany", "berlin"),
    ("Japan", "tokyo"),
])
def test_capital(country, capital, llm_client):
    resp = llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Capital of {country}?"}]
    )
    assert capital in resp.choices[0].message.content.lower()
```

**`pytest.param` — add IDs and marks to individual cases.**

```python
@pytest.mark.parametrize("prompt,expected", [
    pytest.param("2+2?", "4", id="arithmetic"),
    pytest.param("Capital of Mars?", None, id="impossible",
                 marks=pytest.mark.xfail(reason="LLM makes things up")),
])
def test_prompt(prompt, expected, llm_client):
    ...
```

**Built-in markers.**

```python
@pytest.mark.skip(reason="API down in CI")
def test_something(): ...

@pytest.mark.skipif(os.getenv("CI") == "true", reason="no LLM in CI")
def test_real_call(): ...

@pytest.mark.xfail(strict=False, reason="non-deterministic")
def test_flaky(): ...
```

**Custom markers** — register in `pytest.ini` to avoid warnings:

```ini
[pytest]
markers =
    slow: marks tests that make real LLM calls
    expensive: tests that make multiple LLM calls per case
```

**Running pytest in a notebook.** pytest doesn't run inside notebook cells — use this pattern:

```python
# Cell 1
%%writefile test_example.py
import pytest

def test_basic():
    assert 1 + 1 == 2

# Cell 2
!pytest test_example.py -v
```

Exercise: [`exercises/pytest_intro_exercise.md`](exercises/pytest_intro_exercise.md)

---

## DAY 6 — Building a Mini Test Framework (60 min)

### Learning objectives
- Structure a real test project: `tests/`, `conftest.py`, `data/`
- Share fixtures across multiple test files
- Load and evaluate golden datasets from JSON
- Write a consistency test (N runs, at least M must pass)
- Generate HTML reports and run tests in parallel

### Key concepts

**Project structure.**

```
test_framework/
├── conftest.py              ← shared fixtures (pytest auto-discovers)
├── data/
│   └── golden_prompts.json  ← test cases as data, not as code
└── tests/
    ├── test_golden_suite.py  ← parametrized over golden dataset
    ├── test_consistency.py   ← 3-run pass-rate check
    └── test_latency.py       ← timing budgets
```

**Why `conftest.py`?** Fixtures in `conftest.py` are automatically available to all test files in the same directory and subdirectories — without any import. This is pytest's auto-discovery mechanism. Never import from conftest; just request the fixture by name.

**Golden dataset design decisions.**

Why JSON over YAML or a spreadsheet:
- Human-readable and editable without a library
- `json.loads` is stdlib — no dependency
- Trivially parseable in any language → reuse outside pytest
- Version-controlled diffs are clear

Golden case schema:

```json
{
  "id": "unique-kebab-case-id",
  "prompt": "The exact prompt sent to the model",
  "must_include": ["keyword1", "keyword2"],
  "must_not_include": ["forbidden"],
  "min_length": 10,
  "max_length": 1000,
  "expects_refusal": false
}
```

**Parametrizing over a JSON dataset.**

```python
import json
from pathlib import Path
import pytest

CASES = json.loads(Path("data/golden_prompts.json").read_text())

@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_golden(case, llm_client):
    resp = llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": case["prompt"]}],
        temperature=0,
    )
    text = resp.choices[0].message.content
    passed, failures = evaluate_case(case, text)
    assert passed, f"Failures: {failures}"
```

**Consistency testing — run N times, require M passes.**

```python
@pytest.mark.expensive
@pytest.mark.parametrize("prompt, required_term, runs", [
    ("Capital of Germany?", "berlin", 3),
    ("What does CPU stand for?", "processing", 3),
])
def test_consistent_response(prompt, required_term, runs, llm_client):
    responses = []
    for i in range(runs):
        r = llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        responses.append(r.choices[0].message.content.lower())

    hits = sum(1 for r in responses if required_term in r)
    print(f"\n  {hits}/{runs} responses contained '{required_term}'")
    assert hits >= 2, f"Only {hits}/{runs} responses contained '{required_term}'"
```

**Parallel execution.** LLM calls block on the network. `pytest-xdist` runs each test in a worker process:

```bash
pytest -n auto -v    # uses all CPU cores; each test = one worker slot
```

**Reports.**

```bash
pytest -v --html=report.html --self-contained-html --tb=short
```

`--self-contained-html` embeds CSS/JS so the file is fully portable — email it, no broken links.

Exercise: [`exercises/test_framework_exercise.md`](exercises/test_framework_exercise.md)

---

## DAY 7 — CI/CD with GitHub Actions (60 min)

### Learning objectives
- Write a GitHub Actions workflow from scratch
- Understand triggers: `push`, `pull_request`, `schedule`, `workflow_dispatch`
- Store and use API keys as GitHub Secrets
- Cache pip dependencies between runs
- Upload HTML report as a workflow artifact
- Add a `paths:` filter so the workflow only runs when relevant files change
- Set up branch protection to block merges on failing tests

### Key concepts

**Workflow anatomy.** A workflow is a YAML file in `.github/workflows/`. Every field has a job:

```yaml
name: LLM Tests           # display name in Actions tab

on:                        # when to run
  push:
    branches: [main]
    paths:                 # only when these files change
      - "module-02-python-for-ai-testing/**"
      - ".github/workflows/llm-tests.yml"
  pull_request:
    branches: [main]
  schedule:
    - cron: "0 6 * * 1"   # every Monday 6 AM UTC
  workflow_dispatch:        # manual "Run workflow" button

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - uses: actions/cache@v4        # cache pip packages by requirements hash
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

      - run: pip install -r requirements.txt

      - name: Run LLM tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          cd module-02-python-for-ai-testing/examples/test_framework
          pytest -v --html=report.html --self-contained-html

      - uses: actions/upload-artifact@v4   # save report for 90 days
        if: always()                        # upload even if tests failed
        with:
          name: pytest-report
          path: "**/report.html"
```

**Secrets.** Add in: `repo → Settings → Secrets and variables → Actions → New repository secret`. In YAML: `${{ secrets.MY_SECRET }}`. GitHub automatically masks the value in all logs — it prints `***` instead.

**`hashFiles()` cache key.** When `requirements.txt` changes, the cache key changes and pip re-installs. When it hasn't changed, pip skips installation — saves 20–60s per run.

**`if: always()` on artifact upload.** Without this, if tests fail, the upload step is skipped and you can't see the report to debug the failure. `always()` forces the step to run regardless of prior step status.

**Ollama fallback for runs without an OpenAI key.**

```yaml
- name: Start Ollama (fallback)
  if: env.OPENAI_API_KEY == ''
  run: |
    curl -fsSL https://ollama.ai/install.sh | sh
    ollama serve &
    sleep 5
    ollama pull llama3.2:3b
```

**Branch protection = tests with teeth.** Without branch protection, a failing CI run is informational — nothing stops the merge. With it:

1. `Settings → Branches → Add rule`
2. Pattern: `main`
3. Enable: **Require status checks to pass before merging**
4. Add your job name (e.g. `test`)
5. Enable: **Require branches to be up to date before merging**

Now: push to `main` directly is still allowed, but a PR that fails CI cannot be merged.

**Cron syntax reminder.**

```
"0 6 * * 1"
 │ │ │ │ └─ day of week (1 = Monday)
 │ │ │ └─── month (* = every)
 │ │ └───── day of month (* = every)
 │ └─────── hour (6 = 6 AM UTC)
 └───────── minute (0 = top of hour)
```

Exercise: [`exercises/github_actions_exercise.md`](exercises/github_actions_exercise.md)

---

## Module 2 → Module 3 bridge

You now have the Python skills to write tests, a framework to organize them, and a CI pipeline to run them on every change. Module 3 takes the testing discipline deeper — AI-specific test types, what "correctness" even means when the output is probabilistic, and the OWASP LLM Top 10.

---

## Plain-English glossary

| Term | Technical | Plain English |
|---|---|---|
| **Virtual environment** | Isolated Python interpreter + deps tree | A separate kitchen for each project |
| **Package / library** | Reusable code from PyPI | Pre-written code someone else maintains |
| **`isinstance`** | Type check with subclass support | A better `type()` check |
| **f-string** | `f"text {variable}"` | Template literal that evaluates inline |
| **Comprehension** | `[x for x in y if cond]` | One-line loop that builds a list or dict |
| **`*args / **kwargs`** | Variable positional / keyword arguments | Accept any number of extra arguments |
| **`@dataclass`** | Auto-generates `__init__`, `__repr__`, `__eq__` | A struct with batteries |
| **Exception** | Runtime error that halts the normal flow | The "oh crap" moment |
| **`try / except / else / finally`** | Full exception handling block | Prepare → catch → succeed → always |
| **`log.exception()`** | `log.error()` + current traceback | Error log with the crime scene attached |
| **Exponential backoff** | `delay = base * 2^attempt + jitter` | Wait longer after each failure, with randomness |
| **HTTP method** | `GET`, `POST`, `PUT`, `DELETE` | The verb in "please [verb] this resource" |
| **Status code** | 3-digit number describing the response | A one-glance grade on the response |
| **`.env`** | Text file holding secrets, gitignored | A sticky note with your API key kept off the internet |
| **`raise_for_status()`** | Raises `HTTPError` if status >= 400 | "Turn HTTP errors into Python exceptions" |
| **SDK** | Vendor-specific client library | A specialist courier for one shipping company |
| **`LLMResponse`** | Normalized dataclass across providers | A common language all providers speak |
| **pytest** | Python's standard test runner | The judge of your code's behaviour |
| **Fixture** | Reusable setup code via `@pytest.fixture` | Pre-chopped ingredients shared across tests |
| **Fixture scope** | How long a fixture instance lives | `session` = one per run; `function` = one per test |
| **Parametrize** | Run one test with many inputs | One test driven by many datasets |
| **`yield` fixture** | Setup → yield → teardown | A fixture that cleans up after itself |
| **`xfail`** | Expected failure marker | "This is allowed to fail — we know why" |
| **`conftest.py`** | Shared-fixtures file pytest auto-discovers | The pantry — everything in here is available to all recipes |
| **Golden dataset** | Canonical test inputs + expected properties | The answer key you grade responses against |
| **Consistency test** | Run N times, assert M pass | Does the model answer the same way most of the time? |
| **CI / CD** | Continuous Integration / Continuous Delivery | "Run the tests on every change, automatically" |
| **Workflow** | GitHub Actions YAML file | A checklist that runs itself |
| **Job** | Group of steps in a workflow | One station in the workflow kitchen |
| **Step** | Single command in a job | One instruction in the recipe |
| **Secret** | Encrypted value stored in repo settings | A locked envelope only the workflow can open |
| **Artifact** | File produced by a workflow run | The output of the checklist, saved for 90 days |
| **`hashFiles()`** | Cache key based on file content hash | "Cache changes only when requirements.txt changes" |
| **Branch protection** | Rule that blocks merges on failing checks | The bouncer that won't let bad code into main |
| **`cron`** | Time-based scheduler expression | "Run this at 6 AM every Monday" |

---

**Module 2 end state:** you can build a Python project, write tests that hit a real LLM, run them locally with pytest, generate HTML reports, and have everything run automatically in GitHub Actions on every commit. From here, the rest of the course is about making those tests smarter — DeepEval, RAGAS, Promptfoo.
