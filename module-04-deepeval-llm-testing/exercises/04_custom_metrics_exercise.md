# Exercise: GEval & Custom Metrics

**Estimated time:** 40–50 minutes

---

## Part A — Write 3 GEval Criteria (15 min)

Create a `GEval` metric for each of the following evaluation dimensions:

**1. Conciseness**
The response should be concise. A response that rambles, repeats itself, or adds unnecessary caveats should score lower.

**2. Tone formality**
The response should use professional, formal English. No slang, contractions ("can't", "don't"), or casual phrases.

**3. Completeness**
The response should fully answer all parts of the question. A partial answer that ignores part of the question should score lower.

For each `GEval`, write a test case that:
- PASSES the metric (craft an ideal response)
- FAILS the metric (craft a response that violates the criterion)

Run: `pytest exercises/test_geval.py -v`

---

## Part B — Build a Custom `BaseMetric` (15 min)

Write `KeywordCoverageMetric`:

```python
class KeywordCoverageMetric(BaseMetric):
    """
    Checks that all required keywords appear in the actual output.
    score = fraction of required keywords found (0.0–1.0)
    """
    def __init__(self, required_keywords: list[str], threshold: float = 1.0):
        ...
```

- `score = number_found / total_required`
- `reason` = lists which keywords were found and which were missing
- `threshold=1.0` means all keywords must be present to pass
- `threshold=0.7` means 70% coverage is enough

Test it on 3 cases:
1. All keywords present → score = 1.0 → PASS
2. Half keywords present → score = 0.5 → PASS at 0.5 threshold, FAIL at 0.7
3. No keywords present → score = 0.0 → FAIL at any threshold > 0

---

## Part C — Latency Gate (10 min)

Write a test that:
1. Records `start = time.time()` before calling your LLM
2. Records `latency_ms = (time.time() - start) * 1000` after
3. Creates the `LLMTestCase` with `latency=latency_ms / 1000` (seconds)
4. Uses `LatencyMetric(max_seconds=10.0)` to assert the response was fast enough

Run it 3 times and record the latency. Is your model consistently under 10s? Under 5s?

---

## Part D — Combined Metric Suite (5 min)

Combine your custom metrics with DeepEval built-ins for a single "production quality gate":

```python
def quality_gate(case: LLMTestCase) -> None:
    metrics = [
        AnswerRelevancyMetric(threshold=0.7),
        KeywordCoverageMetric(required_keywords=["..."], threshold=0.8),
        LatencyMetric(max_seconds=10.0),
        GEval(name="Conciseness", criteria="...", ...),
    ]
    assert_test(case, metrics)
```

Write 2 cases: one that passes all 4 gates, one that fails at least 1.

---

## Self-Check

- [ ] 3 `GEval` metrics each have a PASS and a FAIL case
- [ ] `KeywordCoverageMetric` returns the right score for all 3 test inputs
- [ ] `metric.reason` lists which keywords were missing
- [ ] Latency test records real call time and gates against a threshold
- [ ] You can explain when `GEval` is better than `CorrectnessMetric`
