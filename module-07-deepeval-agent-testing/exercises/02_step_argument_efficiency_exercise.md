# Exercise: ArgumentCorrectnessMetric + StepEfficiencyMetric + Coverage Matrix

**Estimated time:** 40–50 minutes
**Setup:** `../examples/.env` must be configured. Part A makes live agent calls. Parts B and C work with `golden_dataset.json` and static test cases — no live API calls required if you'd prefer to skip Part A.

---

## Part A — Probe argument contamination and step inefficiency (15 min)

1. **Force argument contamination.** The `run_agent()` function takes a single user message. To simulate a contamination-prone context, construct a system prompt or conversation history that includes a mention of order #12345, then ask about order #67890. One way to do this without modifying `agent_tools.py`: pass a message like "Hi, I called earlier about order #12345 and it was resolved. Now I need help with order #67890 — can I get a refund?" Run this with `verbose=True` and note which `order_id` the agent passes to `process_refund`. Does the context mention of #12345 contaminate the argument? Run `ArgumentCorrectnessMetric` on the result. If the agent correctly extracts `67890`: is that because the metric passed the test, or because this LLM happened to get it right? Would a weaker model fail it? Write your reasoning.

2. **Force step inefficiency.** Ask the agent a vague message with no order number and no product name: `"I'm having a really bad day and nothing is working out."` Run with `verbose=True` and count how many tool calls it makes before (or instead of) escalating. Does it try `check_order_status` or `get_product_info` with empty or guessed arguments before giving up? Run `StepEfficiencyMetric`. If the metric passes (one clean escalation), add a follow-up message that's equally vague but mentions "subscription" to see whether that keyword triggers an unnecessary `get_product_info` call first.

3. **Verify metric independence.** Take the `escalation-01-hardneg` case from `golden_dataset.json`. Run all four metrics on it (`TaskCompletionMetric`, `ToolCorrectnessMetric`, `ArgumentCorrectnessMetric`, `StepEfficiencyMetric`). Which ones pass? Which fails? Does this confirm that `StepEfficiencyMetric` is the only metric sensitive to step count — or does one of the other three also flag it? Explain why the passing metrics pass, not just which ones do.

---

## Part B — Fill two gaps in the coverage matrix (20 min)

The coverage matrix in Day 2's notebook has several `—` (gap) cells. Pick **two** of the following gaps to fill with new golden_dataset.json entries:

**Gap options:**
- `product_inquiry × wrong_argument` — agent calls `get_product_info` but passes a product name pulled from conversation history instead of the one in the current message (e.g., user asks about TurboMax Pro but agent looks up WidgetPro 3000 because it was mentioned earlier)
- `product_inquiry × inefficient_steps` — agent calls `check_order_status` before `get_product_info` for a simple "what does TurboMax Pro cost?" question
- `refund_processing × wrong_tool` — agent calls `check_order_status` instead of `process_refund` when refund is explicitly requested
- `escalation × wrong_argument` — agent calls `escalate_to_human` but passes a `reason` that describes a different issue than the one the customer stated

For each gap you fill:
1. Write the `golden_dataset.json` entry (all required fields, `is_hard_negative=true`)
2. Identify the `eval_type` (which DeepEval metric should fail it)
3. Load it as a `LLMTestCase` and run the targeted metric to verify it fails
4. Update the coverage matrix print block in `02_step_argument_efficiency.ipynb` to change the `—` to `covered` for the cell you filled

---

## Part C — Write a BVA test series for step count (15 min)

Module 4 Day 4 applied BVA to input value ranges. Apply it to **step count** as a numeric dimension:

For the task "check order status and return result to customer":
- **Below minimum** (0 tool calls): agent answers without calling any tool — the Air Canada pattern
- **At minimum** (1 tool call: `check_order_status`) — the expected happy path
- **One above minimum** (2 tool calls): calls `check_order_status` then calls `get_product_info` unnecessarily
- **Well above** (3+ tool calls): the `escalation-01-hardneg` pattern

Construct `LLMTestCase` objects for each step-count boundary (0, 1, 2, 3) using a "What's the status of my order #12345?" input. Run `StepEfficiencyMetric` on each. At what step count does the metric start failing? Is the boundary where you'd expect it? Is a 2-call path for a 1-call task always wrong — or can you construct a scenario where a second tool call for a status query is genuinely justified? If so, does `StepEfficiencyMetric` handle that case correctly?

---

## Self-Check

- [ ] You ran Part A probes against the real agent and can describe actual behavior (not just expected behavior)
- [ ] Your two new golden_dataset.json entries each have a corresponding metric run that confirms failure
- [ ] The coverage matrix in the notebook has been updated to reflect the cells you filled
- [ ] You can explain BVA applied to step count: what are the boundary values, and which metric is sensitive to them
- [ ] You can name the Module 6 hand-rolled verdict that each of today's metrics replaces, and explain why the replacement is less brittle
