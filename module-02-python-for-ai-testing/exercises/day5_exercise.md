# Day 5 — Exercise: Introduction to pytest

**Estimated time:** 40–50 minutes

---

## Part A — First Test Suite (15 min)

Create `exercises/test_day5.py` — a pytest file with at least 8 test functions.

Required tests:
1. `test_classify_temperature` — parametrize over at least 6 temperature values and expected labels.
2. `test_keyword_detection` — parametrize: 5 (response, keyword, should_pass) tuples.
3. `test_empty_response_fails` — assert a zero-length string fails a length check.
4. `test_safe_parse_valid` — assert `safe_parse('{"k": "v"}')` returns a dict.
5. `test_safe_parse_markdown_fence` — assert `safe_parse('```json\n{"k": "v"}\n```')` extracts the dict.
6. `test_safe_parse_no_json` — assert `safe_parse("no json here")` returns `None`.
7. `test_stats_empty_list` — assert `compute_stats([])` returns zeros without crashing.
8. `test_stats_all_pass` — assert pass rate is 100% when all items have `"passed": True`.

Use fixtures where setup is shared (e.g., a `sample_config` fixture). Use `pytest.raises` for at least one test.

---

## Part B — LLM Test Suite (20 min)

Create `exercises/test_day5_llm.py` — tests that make real model calls.

**Session-scoped fixture:** `llm_client` → returns an OpenAI-compatible client.

**Tests (all parametrized):**

1. `test_capital_cities` — parametrize: `[(country, capital), ...]` for at least 5 countries. Assert the capital appears in the response.

2. `test_safety_refusals` — parametrize: 3 harmful prompts. Assert the model refuses (check for refusal signals).

3. `test_consistent_format` — parametrize: 3 prompts that ask for a numbered list (e.g., "List 5 programming languages, numbered"). Assert the response contains `"1."` and `"5."`.

4. `test_latency_budget` — for a simple factual question, assert `time.time()` delta is under 15 seconds.

---

## Part C — Markers & Reports (10 min)

1. Add `@pytest.mark.slow` to all LLM tests in `test_day5_llm.py`.
2. Create a `pytest.ini` in the `exercises/` folder:
   ```ini
   [pytest]
   markers =
       slow: marks tests that make real LLM calls
   ```
3. Run: `pytest test_day5.py -v` (fast, no LLM calls)
4. Run: `pytest test_day5_llm.py -v -m slow` (LLM tests only)
5. Generate HTML report: `pytest -v --html=day5_report.html --self-contained-html`

---

## Self-Check

- [ ] `pytest test_day5.py -v` shows ≥ 8 tests, all green
- [ ] `pytest test_day5_llm.py -v` shows ≥ 4 tests (may have some FAIL — that's OK, explain why)
- [ ] At least one test uses `pytest.raises`
- [ ] At least two tests use `@pytest.mark.parametrize`
- [ ] HTML report opens in a browser and shows pass/fail per test
- [ ] `pytest test_day5.py -m "not slow"` skips the LLM tests correctly
