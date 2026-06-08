# Day 2 — Exercise: Core Metrics Suite

**Estimated time:** 40–50 minutes

---

## Part A — RAG Faithfulness Test (15 min)

Simulate a RAG pipeline: retrieve a context snippet, generate an answer, then test faithfulness.

```python
CONTEXT = [
    "The Eiffel Tower was built between 1887 and 1889 as the entrance arch "
    "for the 1889 World's Fair. It stands 330 metres tall and is located on "
    "the Champ de Mars in Paris, France."
]

PROMPTS = [
    ("How tall is the Eiffel Tower?",            "330 metres"),   # faithful
    ("When was the Eiffel Tower built?",          "1887 to 1889"), # faithful
    ("How many visitors does the Eiffel Tower get per year?",
     "The Eiffel Tower attracts about 7 million visitors annually."), # unfaithful — not in context
]
```

Write `test_faithfulness` parametrized over these cases. Use `FaithfulnessMetric(threshold=0.8)`.

Which case fails? Why? Write your explanation in a comment.

---

## Part B — Hallucination Detection (10 min)

Write `test_no_hallucination` for these three scenarios:

1. **Grounded answer** — the response only uses facts from the context
2. **Partially hallucinated** — mixes real facts with one invented detail
3. **Fully hallucinated** — ignores context, uses only parametric knowledge

Use the same Eiffel Tower context. For cases 2 and 3, craft responses that contain invented numbers or dates. Check that the hallucination metric catches them.

Use `HallucinationMetric(threshold=0.5)` — this means: fail if more than 50% of statements are hallucinated.

---

## Part C — Safety Metrics (10 min)

Write a `test_safety` suite with `ToxicityMetric(threshold=0.5)`:

1. A normal helpful response (should pass)
2. A response containing mildly inappropriate language (should score higher on toxicity)
3. A clearly toxic response (should fail)

For cases 2 and 3, craft realistic-looking but synthetic responses that contain the type of content each scenario describes (no real harmful content — just strings sufficient to trigger the metric).

---

## Part D — Multi-Metric Test (10 min)

Write a single `test_full_evaluation` that evaluates one test case against **all 4 metrics at once**:

```python
metrics = [
    AnswerRelevancyMetric(threshold=0.7),
    FaithfulnessMetric(threshold=0.8),
    HallucinationMetric(threshold=0.5),
    ToxicityMetric(threshold=0.5),
]
assert_test(case, metrics)
```

If any metric fails, `assert_test` raises. Confirm this behavior: write a case where one metric passes and another fails. Observe which one's failure is reported.

---

## Self-Check

- [ ] `FaithfulnessMetric` and `HallucinationMetric` both have tests that fail AND pass
- [ ] You understand the directional difference: Faithfulness (high = good) vs Hallucination (low = good)
- [ ] Multi-metric test raises on the FIRST failing metric
- [ ] You can read `metric.reason` and explain what the judge flagged
- [ ] You can articulate when to use Faithfulness vs Hallucination
