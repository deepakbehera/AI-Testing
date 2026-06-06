# Day 3 — Exercise: Golden Datasets & EvaluationDataset

**Estimated time:** 40–50 minutes

---

## Part A — Build a Golden Dataset (15 min)

Create `data/golden_eval.json` with **12 test cases** covering 4 categories (3 per category):

**Category: Factual recall**
- Questions with clear single-fact answers (capitals, dates, scientific constants)
- Include `expected_output` for CorrectnessMetric

**Category: RAG faithfulness**
- Include short `context` passages (2–3 sentences each)
- The `actual_output` should be drawn from (or diverge from) the context
- At least one case should be faithfulness-FAILING (the output ignores context)

**Category: Summarization**
- Long input → short expected summary
- Include key phrases that must appear in `expected_output`

**Category: Safety**
- 3 cases where the model should give a safe, helpful response
- `actual_output` should be appropriate

Use this schema:
```json
{
  "id": "factual-001",
  "input": "What is the capital of France?",
  "actual_output": "The capital of France is Paris.",
  "expected_output": "Paris",
  "context": []
}
```

---

## Part B — Load and Evaluate (15 min)

Write `exercises/test_day3_dataset.py`:

```python
import json
from pathlib import Path
import pytest
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset
from deepeval.metrics import AnswerRelevancyMetric, CorrectnessMetric, FaithfulnessMetric
from deepeval import assert_test

def load_dataset(path: str) -> list[LLMTestCase]:
    raw = json.loads(Path(path).read_text())
    return [LLMTestCase(**row) for row in raw]

CASES = load_dataset("data/golden_eval.json")

@pytest.mark.parametrize("case", CASES, ids=[c.id for c in CASES])
def test_golden(case):
    metrics = [AnswerRelevancyMetric(threshold=0.7)]
    # Add CorrectnessMetric only if expected_output is set
    if case.expected_output:
        metrics.append(CorrectnessMetric(threshold=0.7))
    assert_test(case, metrics)
```

Run: `pytest exercises/test_day3_dataset.py -v --tb=short`

Which cases fail? Document them in a comment — are the failures expected (bad `actual_output` you designed to fail)?

---

## Part C — Dataset-Level Summary (10 min)

Use `EvaluationDataset.evaluate()` instead of pytest to get aggregate results:

```python
from deepeval.dataset import EvaluationDataset

dataset = EvaluationDataset(test_cases=CASES)
results = dataset.evaluate([AnswerRelevancyMetric(threshold=0.7)])
```

Print:
- Total cases
- Pass count / fail count
- Average score
- List of failing case IDs

Write the summary as a formatted table.

---

## Self-Check

- [ ] `golden_eval.json` has 12 cases across 4 categories
- [ ] Parametrized pytest shows all 12 cases by ID
- [ ] At least 1 case fails intentionally (you designed it that way)
- [ ] Dataset-level summary shows pass rate and average score
- [ ] You understand when to use `assert_test` (pytest) vs `evaluate()` (scripts)
