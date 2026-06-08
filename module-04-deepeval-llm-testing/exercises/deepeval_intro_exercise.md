# Day 1 — Exercise: Your First DeepEval Test

**Estimated time:** 35–45 minutes

---

## Part A — Setup & First Test Case (15 min)

1. Install DeepEval and configure the judge model:
   ```bash
   pip install deepeval
   deepeval set-openai-api-key   # OR set OPENAI_API_KEY in .env
   ```

2. Create `exercises/test_day1.py`. Write a function that calls your LLM, then write a DeepEval test for it:

```python
import os, pytest
from dotenv import load_dotenv
from openai import OpenAI
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric

load_dotenv()
# ... your setup here
```

3. Write `test_answer_relevancy` — a pytest test that:
   - Calls your LLM with the prompt `"What is a large language model?"`
   - Wraps the response in an `LLMTestCase`
   - Asserts it passes `AnswerRelevancyMetric(threshold=0.7)`

4. Run it: `pytest exercises/test_day1.py -v -s`

5. Print `metric.score` and `metric.reason` after measuring. Read the reason — what did the judge say?

---

## Part B — 5 Test Cases (15 min)

Add 4 more test cases covering different question types:

| Prompt | What you're checking |
|---|---|
| `"Explain what a token is in NLP."` | Relevancy on a technical concept |
| `"What is 15 × 13?"` | Relevancy on a math question |
| `"Summarize the plot of Romeo and Juliet in one sentence."` | Relevancy on a creative prompt |
| `"What is the boiling point of water in Celsius?"` | Relevancy on a factual question |

Use `@pytest.mark.parametrize` to run all 5 cases from a single test function.

---

## Part C — Threshold Exploration (10 min)

Pick one test case. Run it with three different thresholds:

```python
for threshold in [0.5, 0.7, 0.9]:
    metric = AnswerRelevancyMetric(threshold=threshold)
    metric.measure(case)
    print(f"threshold={threshold}  score={metric.score:.2f}  passed={metric.passed}")
```

Answer in a comment:
- At what threshold does your case first fail?
- What does that tell you about your LLM's relevancy quality?
- Should your production threshold be 0.5, 0.7, or 0.9 for this use case? Why?

---

## Self-Check

- [ ] `pytest test_day1.py -v` shows at least 5 tests, all pass
- [ ] You can print `metric.score` and `metric.reason` and explain what both mean
- [ ] You understand the difference between `assert_test()` and `metric.measure()`
- [ ] You know what a "judge model" is and why you need one
- [ ] You can explain what threshold=0.7 means in plain English
