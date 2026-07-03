# Exercise: TaskCompletionMetric + ToolCorrectnessMetric

**Estimated time:** 40–50 minutes
**Setup:** `../examples/.env` must be configured (copy `../examples/.env.example` and fill in your credentials). Parts A and C make live LLM calls via `run_agent()` from `../examples/agent_tools.py`. Part B works entirely from `golden_dataset.json` with no API calls.

---

## Part A — Probe the live agent's tool selection behavior (15 min)

The agent uses OpenAI's `tools` parameter — the LLM decides which function to call and what arguments to pass. You cannot force it to pick the wrong tool by changing a boolean, the way Module 6 let you cap `max_hops=1`. Instead, you probe by constructing inputs that make a specific failure *likely*, then check whether it actually happened.

1. **Trigger the Air Canada pattern.** Ask the agent: `"How much does TurboMax Pro cost to cancel?"` Run this with `verbose=True`. Does the agent call `get_product_info`? If it does, does it report the `'unknown'` cancellation fee honestly, or does it rephrase `'unknown'` into something that sounds more like a real answer (e.g., "the fee may vary")? Build a `LLMTestCase` from the response and run `ToolCorrectnessMetric` on it. What score does it receive?

2. **Trigger wrong-tool selection.** Ask the agent: `"Can you cancel my subscription for order #12345?"` There is no `cancel_subscription` tool — the agent must either use `process_refund` (a plausible wrong choice) or `escalate_to_human` (arguably more correct). Run with `verbose=True`. Which tool did it pick? Was that the right choice? Run both `TaskCompletionMetric` and `ToolCorrectnessMetric` on the response. Do they agree?

3. **Test graceful handling of an unknown order.** Ask the agent: `"What's the status of order #55555?"` (not in the database). Does the agent call `check_order_status` (correct) and then report the error honestly, or does it answer without calling a tool? Build a `LLMTestCase` from the response and verify: (a) `ToolCorrectnessMetric` passes (the tool was called), (b) `TaskCompletionMetric` passes (the agent completed the task by honestly reporting an error).

---

## Part B — Extend golden_dataset.json with two new hard negatives (20 min)

Open `../examples/golden_dataset.json` and add two new entries following the exact same schema.

1. **A wrong-tool case for `refund_processing`**: Write a hard negative where a customer asks "I want to cancel and get my money back for order #67890" but the agent calls `check_order_status` instead of `process_refund`. The output should sound plausible — something like "Your order is currently processing and will ship in 5 days." Fill in all required fields: `id`, `category`, `failure_mode`, `is_hard_negative`, `eval_type`, `user_input`, `reference`, `tools_called`, `response`, and `_note`. The `eval_type` should be `"tool_correctness"`.

2. **A wrong-tool case for `escalation`**: Write a hard negative where a customer says "My WidgetPro 3000 is broken and I need help" but the agent calls `check_order_status` (looking for an order) instead of `escalate_to_human` (the appropriate choice when there's no order number and a device issue). Again, fill all fields. `eval_type` should be `"tool_correctness"`.

After adding both entries: load `golden_dataset.json` in a notebook cell, filter to `eval_type="tool_correctness"` hard negatives, convert each to a `LLMTestCase`, and run `ToolCorrectnessMetric`. Both new hard negatives should fail. If one passes, revise its `response` field to make the tool-selection failure more explicit.

---

## Part C — Build a BVA test case for order_id extraction (15 min)

Module 4 Day 4 introduced Boundary Value Analysis. This part applies it to the `order_id` extraction boundary: the edge between "the order_id in the current user message" and "any order_id that appeared anywhere else in the conversation."

Simulate a two-turn conversation where:
- Turn 1: user asks about order #12345 (agent correctly calls `check_order_status('12345')`)
- Turn 2: user asks "actually, can you give me a refund for order #67890 instead?"

For the second turn, construct the `LLMTestCase` to represent what a **boundary-correct** agent does: calls `process_refund('67890', ...)`. Then construct a second case representing the **boundary-incorrect** agent: calls `process_refund('12345', ...)` — the order_id contaminated from turn 1.

Run `ArgumentCorrectnessMetric` on both. Confirm the boundary-incorrect case fails. Write one sentence explaining: in BVA terms, what is the "boundary" here, and what are the "just inside" and "just outside" values?

---

## Self-Check

- [ ] You ran all three live probes in Part A and can describe what actually happened vs. what you expected
- [ ] You can explain why `ToolCorrectnessMetric` and `TaskCompletionMetric` can disagree on the same test case — and which one you'd trust for a tool-bypass failure
- [ ] Your two new golden_dataset.json entries follow the schema correctly (all required fields present, `is_hard_negative=true`, both fail `ToolCorrectnessMetric`)
- [ ] You can define the `order_id` BVA boundary in one sentence without re-reading the notes
