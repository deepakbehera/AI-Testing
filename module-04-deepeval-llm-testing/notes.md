# Module 4 — LLM Testing with DeepEval

**Duration:** 6 hours · split across **6 online sessions of 1 hour each**
**Prerequisites:** Module 2 (pytest, fixtures, parametrize) · Module 3 (AI failure modes, OWASP LLM Top 10)

By the end of this module you will have a full DeepEval test suite that measures hallucination, faithfulness, correctness, toxicity, and bias — running automatically in GitHub Actions on every pull request. Just as importantly, you'll know *how to decide what to test in the first place* — Day 4 is dedicated entirely to that, so the dataset you build on Day 3 gets audited and extended with deliberate, not accidental, coverage.

---

## How the 6 sessions are organized

| Day | Focus | What you'll build |
|---|---|---|
| **1** | DeepEval intro — `LLMTestCase`, first metric | Your first passing DeepEval test |
| **2** | Core metrics deep dive | A suite covering 5 failure modes |
| **3** | Golden datasets & `EvaluationDataset` | A reusable eval dataset with 15+ cases |
| **4** | The testing mindset — test design & coverage | A coverage matrix + 8 adversarial variants from 1 seed case |
| **5** | `GEval` & custom metrics | Criteria-driven evaluation + latency gate |
| **6** | DeepEval in CI | Automated eval pipeline that gates merges |

---

## DAY 1 — Introduction to DeepEval (60 min)

### Learning objectives
- Understand why DeepEval exists and what problem it solves
- Install DeepEval and configure a judge model
- Build an `LLMTestCase` from scratch
- Run your first metric (`AnswerRelevancyMetric`) and read the score
- Understand what "LLM-as-a-judge" means and how scores work

### The problem DeepEval solves

In Module 3 we identified 7 AI failure modes: hallucination, bias, toxicity, prompt sensitivity, regression, model drift, PII leakage. In Module 2 we built tests with pytest `assert`. The gap: **how do you `assert` that a response is not hallucinating?**

You can't write `assert "hallucination" not in response` — the model doesn't announce its hallucinations. You need another model to evaluate the response. That's DeepEval.

> **Plain English:** DeepEval is a test framework where the test assertions are made by an LLM judge, not by string matching. It gives every response a score from 0 to 1 and tells you whether it passed a threshold.

### Architecture

```
Your test suite
    │
    ▼
LLMTestCase(input, actual_output, expected_output, context)
    │
    ▼
Metric(threshold=0.7)   ← e.g. AnswerRelevancyMetric
    │
    ▼
Judge LLM (GPT-4o / Claude / Ollama)
    │
    ▼
score: 0.87   reason: "Response directly addresses..."
passed: True  (0.87 >= 0.7 threshold)
```

### Key concept: `LLMTestCase`

The core object. Every DeepEval test is built around it.

```python
from deepeval.test_case import LLMTestCase

case = LLMTestCase(
    input="What is the capital of France?",         # the prompt sent to your LLM
    actual_output="Paris is the capital of France.",# what your LLM returned
    expected_output="Paris",                         # ground truth (optional — needed for Correctness)
    context=["France is a country in Western Europe. Its capital is Paris."],
    # ^ retrieved documents (needed for Faithfulness / RAG metrics)
)
```

### Key concept: Metrics and thresholds

```python
from deepeval.metrics import AnswerRelevancyMetric

metric = AnswerRelevancyMetric(threshold=0.7)
metric.measure(case)

print(metric.score)   # 0.0–1.0
print(metric.passed)  # True if score >= threshold
print(metric.reason)  # Why the judge gave that score
```

### Key concept: `assert_test` vs `evaluate`

| | `assert_test()` | `evaluate()` |
|---|---|---|
| Use in | pytest | standalone scripts |
| Raises | AssertionError on failure | Returns results dict |
| Output | pytest pass/fail | Summary table |

```python
# In pytest test functions:
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric

def test_capital_question():
    case = LLMTestCase(
        input="What is the capital of France?",
        actual_output="Paris is the capital.",
    )
    metric = AnswerRelevancyMetric(threshold=0.7)
    assert_test(case, [metric])
```

### How LLM-as-a-judge works

The judge LLM receives a structured prompt like:

> *"Given the question: 'What is the capital of France?' and the response: 'Paris is the capital of France.', rate how relevant the response is to the question on a scale of 0–1. Return JSON: {score: float, reason: str}"*

The judge's score becomes the metric score. This is why:
- You need a judge model configured (OpenAI, Ollama, Anthropic)
- The quality of evaluation depends on the judge model's quality
- Use a stronger judge than the model being tested when possible

### Demo you'll see
**`examples/01_deepeval_intro.ipynb`** — setup, first `LLMTestCase`, `AnswerRelevancyMetric`, reading scores and reasons.

Exercise: [`exercises/01_deepeval_intro_exercise.md`](exercises/01_deepeval_intro_exercise.md)

---

## DAY 2 — Core Metrics Deep Dive (60 min)

### Learning objectives
- Use `FaithfulnessMetric` to catch RAG hallucinations
- Use `HallucinationMetric` to detect confabulation
- Use `ToxicityMetric` and `BiasMetric` for safety
- Use `CorrectnessMetric` against a ground-truth answer
- Stack multiple metrics on one test case
- Read and interpret metric `reason` fields

### The 5 core metrics

**1. `AnswerRelevancyMetric`** — Does the response answer the question?

Checks: is the actual output relevant to the input? Catches off-topic rambling, topic drift, and deflection.

```python
from deepeval.metrics import AnswerRelevancyMetric
metric = AnswerRelevancyMetric(threshold=0.7)
# Needs: input, actual_output
```

**2. `FaithfulnessMetric`** — Does the response stick to the provided context?

Designed for RAG pipelines. Catches cases where the model ignores retrieved documents and uses its parametric knowledge instead.

```python
from deepeval.metrics import FaithfulnessMetric
metric = FaithfulnessMetric(threshold=0.8)
# Needs: input, actual_output, context (list of retrieved docs)
```

> **Plain English:** faithfulness is about loyalty to your sources. If the retrieved document says "Berlin has a population of 3.7 million" and the model says "Berlin has a population of 4 million", that's unfaithful — it's diverged from the context.

**3. `HallucinationMetric`** — Does the response contain made-up facts?

Compares the response against provided context. Statements in the response that can't be verified by the context are marked as hallucinations.

```python
from deepeval.metrics import HallucinationMetric
metric = HallucinationMetric(threshold=0.5)
# Score = fraction of statements that ARE hallucinated
# threshold=0.5 means: fail if more than 50% of statements are hallucinated
# Needs: actual_output, context
```

**4. `ToxicityMetric`** — Is the response harmful, offensive, or inappropriate?

```python
from deepeval.metrics import ToxicityMetric
metric = ToxicityMetric(threshold=0.5)
# Score = toxicity level (lower is less toxic)
# Needs: actual_output
```

**5. `CorrectnessMetric`** — Does the response match the expected answer?

Semantic comparison — not exact string match. "Paris" and "Paris, France" both match "Paris" as expected.

```python
from deepeval.metrics import CorrectnessMetric
metric = CorrectnessMetric(threshold=0.7)
# Needs: actual_output, expected_output
```

### Stacking metrics

Every `LLMTestCase` can be evaluated against multiple metrics at once:

```python
case = LLMTestCase(
    input="...", actual_output="...",
    expected_output="...", context=[...]
)
metrics = [
    AnswerRelevancyMetric(threshold=0.7),
    FaithfulnessMetric(threshold=0.8),
    CorrectnessMetric(threshold=0.7),
]
assert_test(case, metrics)
# Passes only if ALL metrics pass
```

### Reading the `reason` field

The reason is the most valuable part of a DeepEval result. It tells you exactly WHY the judge gave a score — priceless for debugging.

```python
metric.measure(case)
print(metric.reason)
# → "The response correctly identifies Paris as the capital but
#    adds unrequested information about the Eiffel Tower, which
#    slightly reduces relevancy to the specific question."
```

### Demo you'll see
**`examples/02_metrics_deep_dive.ipynb`**

Exercise: [`exercises/02_core_metrics_exercise.md`](exercises/02_core_metrics_exercise.md)

---

## DAY 3 — Golden Datasets & `EvaluationDataset` (60 min)

### Learning objectives
- Load test cases from a JSON golden dataset
- Use `EvaluationDataset` to run metrics across many cases
- Understand dataset-level pass rates and summaries
- Use DeepEval's built-in synthesizer to generate test cases
- Integrate `EvaluationDataset` with pytest via `@pytest.mark.parametrize`

### From one test case to a dataset

A single `LLMTestCase` is a unit test. An `EvaluationDataset` is a test suite. The dataset holds multiple cases and runs metrics across all of them, producing aggregate stats (pass rate, average score, failure list).

```python
from deepeval.dataset import EvaluationDataset

dataset = EvaluationDataset(test_cases=[case1, case2, case3])
dataset.evaluate([AnswerRelevancyMetric(threshold=0.7)])
```

### Loading from JSON

Your golden dataset JSON format:

```json
[
  {
    "id": "capitals-001",
    "input": "What is the capital of France?",
    "actual_output": "Paris is the capital of France.",
    "expected_output": "Paris",
    "context": ["France's capital city is Paris, known as the City of Light."]
  }
]
```

Loading:

```python
import json
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset

raw = json.loads(Path("golden.json").read_text())
cases = [LLMTestCase(**row) for row in raw]
dataset = EvaluationDataset(test_cases=cases)
```

### Using the synthesizer

DeepEval can generate test cases from your documents automatically:

```python
from deepeval.synthesizer import Synthesizer

synthesizer = Synthesizer()
dataset = synthesizer.generate_goldens_from_docs(
    document_paths=["your_docs/faq.pdf"],
    max_goldens_per_document=10,
)
```

### pytest integration with `EvaluationDataset`

```python
# conftest.py
@pytest.fixture(scope="session")
def eval_dataset():
    raw = json.loads(Path("data/golden.json").read_text())
    return [LLMTestCase(**row) for row in raw]

# test_golden_suite.py
@pytest.mark.parametrize("case", eval_dataset, ids=[c.id for c in eval_dataset])
def test_golden(case):
    assert_test(case, [AnswerRelevancyMetric(threshold=0.7)])
```

### Demo you'll see
**`examples/03_golden_datasets.ipynb`**

Exercise: [`exercises/03_golden_datasets_exercise.md`](exercises/03_golden_datasets_exercise.md)

---

## DAY 4 — The Testing Mindset (60 min)

### Learning objectives
- Explain why a "happy path only" dataset gives a false sense of confidence
- Name 8 distinct types of testing for LLM systems and when each applies
- Apply equivalence partitioning and boundary value analysis to prompts and context
- Build a coverage matrix mapping capabilities to Module 3's failure modes
- Turn one seed test case into 8 targeted adversarial variants
- Design a "hard negative" case and explain why a dataset needs at least one

### Why this day exists

Day 3 had you build a real `golden_eval.json` by hand. Without a deliberate design process behind it, a golden dataset drifts toward whatever is easiest to write: well-formed questions the model is obviously good at. That produces a high pass rate and very little signal. Today gives you the process to audit and extend what you already built.

> **Plain English:** giving someone a stopwatch doesn't make them a good race official if they don't know where to put the finish line. Day 1-3 gave you the stopwatch (metrics, a dataset). Today is about where to put the finish line.

### Types of testing for an LLM system

| Type | Question it answers | Where it's covered |
|---|---|---|
| Functional / happy-path | Does it work when everything goes right? | Day 1-3 |
| Edge-case / boundary | Does it work at the limits of valid input? | Today |
| Adversarial / red-team | Can it be made to misbehave on purpose? | Module 3 Day 3 |
| Metamorphic / consistency | Does meaning-preserving rephrasing change the answer? | Module 3 Day 1 |
| Differential | Does this version differ from the last one? | Module 8 |
| Regression | Did a change break something that used to work? | Day 3, Day 6 |
| Safety / fairness | Does behavior change unfairly or unsafely under pressure? | Module 3 Day 2-3 |
| Load / latency | Does it respond acceptably under real-world timing? | Day 5 |

### Equivalence partitioning & boundary value analysis

Group prompts into classes (input length, context availability, question structure, language/formality, domain fit) and test one representative per class — then specifically test the *edges* of each class, since bugs cluster there (the token-budget boundary, "just enough context" vs. "missing the one needed sentence", the line a refusal policy draws).

### The coverage matrix

A simple table: rows are capabilities/scenarios, columns are Module 3's failure modes, cells are case counts. The point isn't 100% density — it's making silent gaps on high-risk intersections visible instead of accidental.

### Seed case → 8 variants

Given one happy-path case, systematically mutate it: paraphrase, negation, distractor context, missing context, contradictory context, adversarial framing, format stress, out-of-scope. This is the fastest way to turn 1 case into a coverage cluster, and it reuses Module 3's red-team thinking at the dataset-design stage instead of as a one-off probe.

### Hard negatives

A case deliberately built so the *correct* behavior is for it to fail a metric (e.g., a faithfulness check on a response with a fabricated number). If your dataset has zero of these, you can't tell "the model is great" apart from "the metric can't detect failure" — the same logic as mutation testing in traditional software QA.

### Annotating the golden dataset schema

Add `category`, `failure_mode`, and `is_hard_negative` fields to dataset rows on top of Day 3's base schema. They're inert to `LLMTestCase`/`EvaluationDataset` (extra keys are ignored) but let a script regenerate the coverage matrix straight from the dataset file. Go back and retrofit Day 3's `golden_eval.json` with them.

### Demo you'll see
**`examples/04_testing_mindset.ipynb`**

Exercise: [`exercises/04_testing_mindset_exercise.md`](exercises/04_testing_mindset_exercise.md)

---

## DAY 5 — `GEval` & Custom Metrics (60 min)

### Learning objectives
- Write evaluation criteria in plain English with `GEval`
- Build a custom metric by subclassing `BaseMetric`
- Add a `LatencyMetric` (non-LLM metric)
- Combine LLM-judge metrics and rule-based metrics
- Understand when to use each type

### `GEval` — criteria-driven evaluation

`GEval` lets you define what "good" means in plain English, without writing Python logic. The judge LLM interprets your criteria and scores accordingly.

```python
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

conciseness = GEval(
    name="Conciseness",
    criteria="The response should be concise and not contain unnecessary information.",
    evaluation_params=[
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.INPUT,
    ],
    threshold=0.7,
)
```

> **Plain English:** `GEval` is like writing a marking rubric for the judge. "A good answer is concise and directly addresses the question. Score it 0–1 based on how well the answer meets this rubric."

**Good `GEval` criteria include:**
- Single, clear concept to evaluate (not "good in all ways")
- Explicit guidance on what would score high vs low
- Reference to the specific input/output parameters

```python
# Good: specific and single-dimension
"The response should be written in formal English, avoiding slang and contractions."

# Bad: too vague, multi-dimensional
"The response should be good."
```

### Custom `BaseMetric`

For rule-based checks that don't need an LLM judge:

```python
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase

class LengthMetric(BaseMetric):
    def __init__(self, max_chars: int = 500, threshold: float = 1.0):
        self.max_chars = max_chars
        self.threshold = threshold
        self.name = "LengthMetric"

    def measure(self, test_case: LLMTestCase) -> float:
        length = len(test_case.actual_output)
        self.score = 1.0 if length <= self.max_chars else 0.0
        self.reason = (
            f"Response is {length} chars "
            f"({'within' if self.score else 'exceeds'} {self.max_chars} limit)"
        )
        return self.score

    def is_successful(self) -> bool:
        return self.score >= self.threshold

    async def a_measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:
        return self.measure(test_case)
```

### `LatencyMetric`

Measure response time as a metric:

```python
from deepeval.metrics import LatencyMetric

metric = LatencyMetric(max_seconds=5.0)
# Built-in — checks test_case.latency_ms / 1000 <= max_seconds
# Needs: test_case.latency (set when running your LLM call)
```

### Demo you'll see
**`examples/05_custom_metrics.ipynb`**

Exercise: [`exercises/05_custom_metrics_exercise.md`](exercises/05_custom_metrics_exercise.md)

---

## DAY 6 — DeepEval in CI/CD (60 min)

### Learning objectives
- Write a GitHub Actions workflow that runs DeepEval evals on every push
- Store judge model API keys as GitHub Secrets
- Gate pull request merges on eval pass rates
- Upload the DeepEval HTML report as an artifact
- Understand the difference between unit tests (fast) and eval runs (slow/expensive)

### Workflow structure

```yaml
# .github/workflows/llm-eval.yml
name: LLM Evaluation

on:
  push:
    branches: [main]
    paths: ["module-04-deepeval-llm-testing/**"]
  pull_request:
    branches: [main]
  schedule:
    - cron: "0 2 * * 1"   # nightly Monday 2 AM UTC

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
      - run: pip install -r module-04-deepeval-llm-testing/requirements.txt
      - name: Run DeepEval suite
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          cd module-04-deepeval-llm-testing
          pytest tests/ -v --tb=short
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: deepeval-report
          path: "**/*.html"
```

### Gating merges on eval scores

With branch protection enabled (`Settings → Branches → Require status checks`), if the DeepEval pytest suite fails (any metric below threshold), the PR cannot be merged.

**Threshold strategy:**
- Start loose (threshold=0.5) and tighten as you learn your model's baseline
- Different metrics deserve different thresholds: Faithfulness 0.8+, Toxicity 0.3 (lower is less toxic), Relevancy 0.7+
- Keep expensive multi-metric cases in a `@pytest.mark.expensive` group and run them only on schedule, not on every push

### Scheduled regression runs

```yaml
schedule:
  - cron: "0 2 * * 1"   # every Monday 2 AM
```

Run the full eval suite weekly to detect **model drift** — degradation in quality without any code change (e.g., OpenAI silently updated a model).

### Demo you'll see
**`examples/06_ci_integration/llm-eval.yml`**

Exercise: [`exercises/06_cicd_exercise.md`](exercises/06_cicd_exercise.md)

---

## Module 4 → Module 5 bridge

You now have a framework that evaluates LLM responses on relevancy, faithfulness, correctness, and safety — and runs it automatically in CI. Module 5 takes the faithfulness and context metrics deeper: RAGAS is purpose-built for RAG pipelines, with metrics for retrieval precision, context recall, and answer groundedness.

---

## Plain-English Glossary

| Term | Technical | Plain English |
|---|---|---|
| **DeepEval** | Open-source LLM eval framework | pytest + LLM judge combined |
| **`LLMTestCase`** | Dataclass: input, output, context, expected | The "patient file" for one eval |
| **`EvaluationDataset`** | Collection of `LLMTestCase` objects | A test suite for the LLM |
| **Metric** | A measurable quality dimension | One report card item |
| **Threshold** | Minimum passing score (0–1) | The passing grade |
| **Score** | 0.0–1.0 quality rating from judge | The actual grade |
| **Reason** | Judge's explanation of the score | The teacher's comment |
| **LLM-as-a-judge** | Using an LLM to evaluate another LLM | A peer review system |
| **`AnswerRelevancyMetric`** | Does the response address the question? | Is it on topic? |
| **`FaithfulnessMetric`** | Does the response stick to context? | Does it use its sources? |
| **`HallucinationMetric`** | Does the response invent facts? | Is it making things up? |
| **`ToxicityMetric`** | Is the response harmful? | Is it safe to show users? |
| **`CorrectnessMetric`** | Does the response match ground truth? | Is the answer right? |
| **`GEval`** | Criteria-driven evaluation in plain English | Your own rubric |
| **`BaseMetric`** | Abstract class for custom metrics | Build your own judge |
| **`LatencyMetric`** | Response time gate | Was it fast enough? |
| **`assert_test()`** | Raises on metric failure, used in pytest | The pytest integration point |
| **`evaluate()`** | Runs dataset evals, returns summary | The batch eval runner |
| **Model drift** | Silent quality degradation over time | The model got worse without warning |
| **Synthesizer** | Auto-generates test cases from docs | The test data factory |
| **Judge model** | LLM used to evaluate responses | The examiner |
| **Gating** | Blocking merges on failing evals | The CI bouncer |
| **Equivalence partitioning** | Grouping inputs into classes expected to behave alike | Testing one student per class instead of every student |
| **Boundary value analysis** | Testing the edges of an equivalence class, not the middle | Checking the pothole at the edge of the road, not the smooth center |
| **Coverage matrix** | Table of capability × failure mode, cells = test case counts | A checklist that shows which combinations you forgot to test |
| **Hard negative** | A case deliberately built to fail a metric | A planted bug to prove your smoke detector actually works |
| **Metamorphic testing** | Checking that meaning-preserving input changes don't change the verdict | Asking the same question 5 ways and expecting 5 consistent answers |
| **Differential testing** | Comparing outputs of two versions on the same inputs | Diffing model v1 vs v2 like a code diff |
// test edit
