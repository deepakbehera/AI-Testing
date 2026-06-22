# Exercise: The Testing Mindset

**Estimated time:** 45–55 minutes

---

## Part A — Equivalence Classes & Boundary Values (15 min)

Pick one capability from your own project (or use "answers questions about a product's shipping policy" if you don't have one handy).

1. Define at least 4 equivalence-partition dimensions for it (e.g. input length, context availability, question structure, language/formality) — model this on the `partitions` dict from `examples/04_testing_mindset.ipynb`.
2. For each dimension, write 3-5 named classes (e.g. `empty`, `very_short`, `normal`, `boundary_long`).
3. Pick one boundary value to test per dimension — the point right at the edge of a class, not the comfortable middle.
4. Write a short comment for each boundary explaining *why* that exact point is risky (e.g. "right at the token budget — one token over may silently truncate context").

---

## Part B — One Seed Case → Eight Variants (15 min)

Using the `generate_variants()` pattern from the notebook, take this seed case:

```python
seed = {
    "id": "support-hours-00",
    "input": "What are your customer support hours?",
    "context": ["Support is available Monday-Friday, 9am-6pm EST, excluding public holidays."],
}
```

Produce variants covering **all** of these mutation families:

1. Paraphrase
2. Negation
3. Distractor context (add 2 unrelated context sentences)
4. Missing context (drop the context entirely)
5. Contradictory context (add a second context sentence that disagrees with the first)
6. Adversarial framing (try to get the model to assert something false about support hours)
7. Format stress (typos, ALL CAPS, or no punctuation)
8. Out-of-scope (ask about a different company's support hours)

For each variant, write one sentence: *what specific failure is this designed to surface?*

---

## Part C — Build a Coverage Matrix (10 min)

Take the 8 variants from Part B (plus the original seed) and annotate each with:
- `category` (pick one: `factual_recall`, `policy_qa`, `safety_refusal`, or define your own)
- `failure_mode` (pick from Module 3's seven: hallucination, bias, toxicity, prompt_sensitivity, regression, model_drift, pii_leakage — or `prompt_injection` for the adversarial one)

Build the `category` × `failure_mode` matrix (reuse the `Counter`-based code from the notebook). Identify at least one cell that's at `0` and decide: is that an acceptable gap, or a real hole in your coverage? Write one sentence justifying your answer either way.

---

## Part D — Write a Hard Negative (10 min)

Write **one** test case where the `actual_output` is deliberately wrong in a way a faithfulness-style check should catch — using the support-hours context from Part B.

1. Write the fabricated `actual_output` (e.g. invents different hours, or a guarantee the context never made).
2. Using the `keyword_faithfulness_check()` pattern from the notebook (or your own simple rule), confirm it actually flags the case as a FAIL.
3. If your check does **not** flag it: that's a real finding. Write one sentence explaining why the check missed it and what you'd change.

---

## Self-Check

- [ ] You can name all 8 types of testing from Section 1 of the notebook and give one example of each from your own project
- [ ] You have at least one boundary-value test per equivalence dimension, not just a middle-of-the-road example
- [ ] Your 8 variants each target a *different* mutation family — no duplicates
- [ ] Your coverage matrix has at least one identified gap, with a written justification for whether it matters
- [ ] Your hard negative case actually fails your check — if it doesn't, you've found a gap in the check itself, not just the dataset
