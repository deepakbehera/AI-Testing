# Exercise: Tool/Memory Validation, Multi-Hop Reasoning & Failure-Path Testing

**Estimated time:** 40–50 minutes

---

## Part A — Partial Memory Loss (10 min)

Write a third case for `facts_present_in_answer()` where the final answer reflects hop 1's fact (`"WidgetPro 3000"`) but drops a *second* required fact you define yourself (e.g. the discontinuation year, `"2023"`). Does the function correctly flag only the missing one, not both? What does this tell you about checking multiple required facts independently versus checking for "memory loss" as a single yes/no question?

---

## Part B — A New Reasoning-Chain Break (15 min)

Construct your own `reasoning_chain_break` hard negative in a domain other than product fees — dates, locations, or prices all work well.

1. Write 2 retrieved facts that are each individually true and grounded.
2. Write a response that combines them incorrectly (right facts, wrong conclusion) — model it on the WidgetPro fee-swap example.
3. Write the check function that catches it, following the `check_correct_product_fee()` pattern.
4. Run a faithfulness-style check (like Module 5 Day 3's `keyword_faithfulness_check()`) against your hard negative. Confirm it incorrectly passes — that's the point being demonstrated.

---

## Part C — Closing the `premature_stop` Gap (10 min)

Day 2's coverage matrix had `multi_hop_qa` × `premature_stop` sitting at `0`.

1. Take the premature-stop bug you built in Day 1's Try-It-Yourself Part 1 and turn it into a properly annotated case (`id`, `category`, `failure_mode`, `is_hard_negative`) for `annotated_cases`.
2. Recompute the coverage matrix. Confirm the cell is no longer `0`.
3. Is there still a `0` cell left? Decide, in one sentence, whether it's an acceptable gap for this small example dataset or a real one.

---

## Part D — Graceful Failure, Adversarially (10 min)

Write a response that is **ungraceful** but doesn't contain an obviously invented number — e.g. it confidently restates an *old* fact as if it were current, rather than fabricating a new one. Does `empty_hop_response_is_graceful()` catch it? What does this tell you about the limits of keyword-based hedge-phrase detection, and what would a more robust check need to look at instead?

---

## Self-Check

- [ ] Your partial-memory-loss case correctly identifies which specific fact is missing, not just that something is
- [ ] Your reasoning-chain-break hard negative passes a faithfulness check but fails your combination-aware check — and you can explain why in one sentence
- [ ] The `premature_stop` cell in your coverage matrix is no longer `0`
- [ ] You found at least one ungraceful response that your hedge-phrase check misses, and can explain the gap
