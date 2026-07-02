# Exercise: Tool/Memory Validation, Multi-Hop Reasoning & Failure-Path Testing

**Estimated time:** 40–50 minutes
**Setup:** `../examples/.env` must be configured — Parts A and D compare against the real agent's actual answers from the Day 2 notebook.

---

## Part A — Partial Memory Loss (10 min)

Write a third case for `facts_present_in_answer()` where the final answer reflects hop 1's fact (`"WidgetPro 3000"`) but drops a *second* required fact you define yourself (e.g. the discontinuation year, `"2023"`). Does the function correctly flag only the missing one, not both? What does this tell you about checking multiple required facts independently versus checking for "memory loss" as a single yes/no question?

---

## Part B — A New Reasoning-Chain Break (15 min)

Construct your own `reasoning_chain_break` hard negative in a domain other than product fees — dates, locations, or prices all work well.

1. Add a normal/hard-negative pair to `../examples/golden_dataset.json` with `eval_type: "reasoning"`, `must_include`, and `must_not_include` fields (model it on `multi-hop-widgetpro-01` / `multi-hop-widgetpro-01-hardneg`).
2. Write your own version of `check_correct_product_fee()` (the Day 2 notebook's pattern) for your new domain. Confirm it passes your normal case and fails your hard negative.
3. Run Module 5 Day 3's `keyword_faithfulness_check()` against your hard negative's retrieved facts and response. Confirm it passes despite the answer being wrong — that's the exact gap a reasoning-level check exists to cover.

---

## Part C — Closing the `query_drift` Gap (10 min)

Day 1's failure-mode table names `query_drift` but `../examples/golden_dataset.json` has no row for it yet — unlike `premature_stop`, which the course dataset already covers (see `multi-hop-turbomax-01`).

1. Design a `query_drift` case: a question where a plausible-but-wrong hop-2 reformulation would pull the retriever toward an unrelated fact. Add a hard-negative row with the drifted `retrieved_contexts` and the wrong `response` that would result.
2. Recompute the coverage matrix (Day 2 notebook, the cell that reads `golden_dataset.json`). Confirm the `query_drift` cell is no longer `0`.
3. Is there still a `0` cell left afterward? Decide, in one sentence, whether it's an acceptable gap for this course-sized dataset or a real one.

---

## Part D — Graceful Failure, Adversarially (10 min)

Write a response that is **ungraceful** but doesn't contain an obviously invented number — e.g. it confidently restates an *old* fact as if it were current, rather than fabricating a new one. Does `empty_hop_response_is_graceful()` (defined in the Day 2 notebook) catch it? What does this tell you about the limits of keyword-based hedge-phrase detection, and what would a more robust check need to look at instead?

---

## Self-Check

- [ ] Your partial-memory-loss case correctly identifies which specific fact is missing, not just that something is
- [ ] Your reasoning-chain-break hard negative passes a faithfulness-style keyword check but fails your combination-aware check — and you can explain why in one sentence
- [ ] The `query_drift` cell in your coverage matrix is no longer `0`
- [ ] You found at least one ungraceful response that your hedge-phrase check misses, and can explain the gap
