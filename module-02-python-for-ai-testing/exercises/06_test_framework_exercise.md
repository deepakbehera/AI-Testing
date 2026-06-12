# Exercise: Building a Mini Test Framework

**Estimated time:** 45–60 minutes

---

## Goal

Extend the `test_framework/` with new test cases, a new test module, and enhanced reporting.

---

## Part A — Expand the Golden Dataset (15 min)

Open `test_framework/data/golden_prompts.json`. Add **8 new test cases** — at least 2 from each category:

**Category: Translation**
- Ask the model to translate a word to another language. Assert the expected translation appears.

**Category: Math**
- Ask a multi-step math question. Assert the numeric answer appears.

**Category: Format enforcement**
- Ask the model to respond in a specific format (e.g., bullet points with `•`, a numbered list, a haiku). Assert format markers appear.

**Category: Safety**
- Two prompts that should be refused. Set `"expects_refusal": true`.

**Run the suite** and confirm all new cases appear in the output:
```bash
cd 06_test_framework && pytest -v
```

---

## Part B — New Test Module: Consistency (20 min)

Create `test_framework/tests/test_consistency.py`.

This module runs each prompt **3 times** and asserts that the key term appears in at least 2 of 3 responses.

```python
@pytest.mark.parametrize("prompt, required_term, runs", [
    ("What is the capital of Germany?",   "berlin",      3),
    ("What does CPU stand for?",          "processing",  3),
    ("Name the author of Romeo and Juliet.", "shakespeare", 3),
])
def test_consistent_response(prompt, required_term, runs, llm_client):
    ...
```

The test should:
- Record all 3 responses.
- Count how many contain `required_term`.
- Assert count >= 2 (at least 2/3 must pass).
- Print a summary (use `-s` flag when running).

---

## Part C — Latency Budgets (10 min)

Add to `test_framework/tests/test_latency.py` (already exists) or create it:

```python
@pytest.mark.parametrize("prompt, max_ms", [
    ("What is 2+2?",                           5000),
    ("Translate 'hello' to French.",            8000),
    ("List the planets in the solar system.",  10000),
])
def test_latency_within_budget(prompt, max_ms, llm_client):
    ...
```

---

## Part D — Enhanced Reporting (10 min)

1. Run the full suite with parallel execution and generate a report:
   ```bash
   cd 06_test_framework
   pytest -n auto -v --html=full_report.html --self-contained-html --tb=short
   ```
2. Open `full_report.html`. Take a screenshot or note:
   - Total tests run
   - Total pass / fail
   - Slowest test (highest duration)
   - Which test (if any) failed and why

3. Add a custom pytest marker `@pytest.mark.expensive` to the consistency tests (they make 3× more API calls). Document it in `pytest.ini`:
   ```ini
   markers =
       expensive: tests that make multiple LLM calls per case
   ```

---

## Self-Check

- [ ] Golden dataset has ≥ 8 new cases across 4 categories
- [ ] All existing tests still pass after adding new cases
- [ ] `test_consistency.py` runs and shows per-run results with `-s`
- [ ] Latency tests have sensible budgets for your model/provider
- [ ] HTML report shows all test results in one file
- [ ] You can run only consistency tests: `pytest -m expensive -v`
