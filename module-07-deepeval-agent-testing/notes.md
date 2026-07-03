# Module 7 — AI Agents Testing with DeepEval

**Duration:** 2 hours · split across **2 online sessions of 1 hour each**
**Prerequisites:** Module 4 (DeepEval, golden datasets, **the testing mindset — Day 4**) · Module 6 (agentic RAG, LangSmith tracing, hand-rolled LLM judges)

Module 6 gave you a working multi-hop agent and three hand-rolled verdict functions: `MemoryRetentionVerdict`, `ReasoningChainVerdict`, and `GracefulFailureVerdict`. Those were intentional placeholders — building them by hand makes you think clearly about what each one is really measuring. Now we replace them with DeepEval's purpose-built agent metrics: the same test cases, the same failure modes, the same equivalence partitions from Module 4 Day 4 — but running through a proper, reusable framework instead of bespoke string-matching logic. The agent also gains something new: real tool-calling (not just retrieval). That means the test surface expands to cover not just *what the agent said* but *which tool it picked* and *what arguments it passed*.

---

## How the 2 sessions are organized

| Day | Focus | What you'll build |
|---|---|---|
| **1** | TaskCompletionMetric + ToolCorrectnessMetric | A tool-calling customer service agent and DeepEval test cases verifying the agent picks the right tool |
| **2** | ArgumentCorrectnessMetric + StepEfficiencyMetric + coverage matrix | Hard negatives for wrong arguments and inefficient call chains; a complete coverage matrix replacing Module 6's hand-rolled checks |

---

## DAY 1 — TaskCompletionMetric + ToolCorrectnessMetric (60 min)

### Learning objectives
- Explain how real tool-calling (function-calling API) differs from retrieval-based agentic RAG
- Map Module 6's three hand-rolled verdict functions to their DeepEval equivalents
- Build `LLMTestCase` objects with `ToolCall` records and run `TaskCompletionMetric` and `ToolCorrectnessMetric`
- Apply Module 4 Day 4 equivalence partitioning to "tool selection" as a new dimension (same technique, new axis)
- Understand why Air Canada was found liable for its chatbot in February 2024 and how `ToolCorrectnessMetric` would have caught it

### From retrieval-based agents to tool-calling agents

Module 6's agent had one "tool": a retriever that queried a corpus. The planner decided when to retrieve; the generator wrote the final answer. Testing it required checking whether the *answer* was correct (faithfulness, reasoning chain).

A tool-calling agent is different in one important way: the LLM now selects a function by name and supplies its arguments. The LLM does not just decide *when* to act — it decides *what to do* and *how to parameterize it*. That opens three new failure categories that Module 6's tests couldn't see:

```
User: "What's the status of order #12345?"

Module 6 agent path:
  query → retrieve("order 12345 status") → generate answer
  TEST: is the answer faithful to what was retrieved?

Module 7 agent path:
  user_input → LLM selects tool: check_order_status(order_id="12345") → tool executes → LLM generates answer
  TESTS: (1) did it pick the right tool?  (2) did it pass the right arguments?
         (3) did it complete the task with the minimum number of tool calls?
```

> **Plain English:** Module 6 tested a research assistant who chose which bookshelf to search. Module 7 tests a customer service rep who can actually do things — look up orders, issue refunds, get product specs, escalate calls. Getting the right answer matters, but so does *what action they took to get there* and *what they typed into the system*.

### Mapping Module 6's hand-rolled checks to DeepEval

| Module 6 hand-rolled verdict | What it measured | DeepEval replacement |
|---|---|---|
| `GracefulFailureVerdict` | Did the agent admit uncertainty instead of hallucinating? | `TaskCompletionMetric` — did the agent accomplish the stated task at all? |
| `ReasoningChainVerdict` | Did the agent follow a valid reasoning path? | `ToolCorrectnessMetric` — did the agent call the right tool(s)? |
| `MemoryRetentionVerdict` | Did an early-hop fact survive to the final answer? | `ArgumentCorrectnessMetric` — did the agent pass the right arguments to each tool? (Day 2) |

None of these are exact 1-to-1 replacements — they measure adjacent things. The point of the mapping is to show continuity: you already understand the *problem* each one solves. DeepEval gives you a standardized, LLM-judged, threshold-able version that doesn't need to be rewritten for each new agent.

### Real incident: Air Canada chatbot grief discount hallucination (February 2024)

Air Canada deployed an AI support chatbot that a grieving passenger asked about bereavement fares. The chatbot told him that bereavement discounts could be claimed *retroactively* after a flight — which was incorrect. Air Canada's actual policy required applying before travel. The airline was taken to Canada's Civil Resolution Tribunal and lost: the court ruled the chatbot's misleading statement was binding on the airline even though the correct policy was also posted on their website.

The failure was specifically a **wrong tool** failure: the bot *answered a policy question from memory* rather than calling a tool like `get_current_policy(topic="bereavement_fares")`. In our agent's vocabulary, it chose to generate an answer from its parametric knowledge instead of calling `get_product_info`. There was no tool call to inspect; there was no `ToolCall` record to audit. That's what `ToolCorrectnessMetric` catches — not that the answer was wrong, but that the agent *skipped the tool that would have given it the correct answer*.

> **Why this matters for today:** Air Canada's legal team argued the chatbot was a "separate legal entity" responsible for its own statements. The tribunal rejected that. The lesson: when your agent answers policy questions without calling the authoritative tool, you own the answer. `ToolCorrectnessMetric`'s job is to catch agents that bypass the tool.

### The customer service agent: tools and in-memory database

`examples/agent_tools.py` builds a customer service agent around four real tools and an in-memory "database." The same WidgetPro/TurboMax theme from Module 6, extended with order management:

```python
# In-memory databases (from agent_tools.py)
ORDERS = {
    "12345": {"status": "shipped",    "product": "WidgetPro 3000",  "estimated_delivery": "2 days",  "amount": 199.00},
    "67890": {"status": "processing", "product": "TurboMax Pro",    "estimated_delivery": "5 days",  "amount": 299.00},
    "99999": {"status": "delivered",  "product": "WidgetPro 3000",  "estimated_delivery": None,      "amount": 199.00},
}
PRODUCTS = {
    "WidgetPro 3000":  {"price": "$199",         "cancellation_fee": "$0",      "support_type": "online"},
    "TurboMax Pro":    {"price": "$299/year",     "cancellation_fee": "unknown", "support_type": "online"},
    "WidgetPro 2000":  {"price": "discontinued",  "cancellation_fee": "$50",     "support_type": "none"},
}
```

The four tools the agent can call:

```python
def check_order_status(order_id: str) -> dict:
    # Returns {"status": ..., "product": ..., "estimated_delivery": ...}
    # Returns {"error": "Order not found"} for unknown IDs

def process_refund(order_id: str, reason: str) -> dict:
    # Returns {"refund_id": ..., "amount": ..., "status": "initiated"}

def get_product_info(product_name: str) -> dict:
    # Returns {"price": ..., "cancellation_fee": ..., "support_type": ...}

def escalate_to_human(reason: str) -> dict:
    # Returns {"ticket_id": ..., "estimated_wait": ..., "queue": "billing"|"technical"|"general"}
```

Each tool is decorated with `@traceable` — every tool invocation appears as its own LangSmith span. When something goes wrong, you can see exactly which tool was called, with what arguments, and what it returned — without instrumenting anything extra.

### The agent loop: how real tool-calling works

Unlike Module 6's retrieval loop (which the agent controlled), real tool-calling puts the LLM in charge of function selection via OpenAI's `tools` parameter:

```python
# Simplified from agent_tools.py
async def run_agent(user_message: str) -> AgentResponse:
    messages = [{"role": "user", "content": user_message}]
    tool_calls_made = []

    # Step 1: send user message + tool definitions to the LLM
    response = await _client.chat.completions.create(
        model=_llm_model,
        messages=messages,
        tools=TOOL_DEFINITIONS,          # the 4 tools, in OpenAI function-calling format
        tool_choice="auto",
    )

    # Step 2: LLM returns a tool call (name + arguments JSON)
    tool_call = response.choices[0].message.tool_calls[0]
    tool_name = tool_call.function.name
    tool_args = json.loads(tool_call.function.arguments)

    # Step 3: execute the tool
    result = TOOL_MAP[tool_name](**tool_args)
    tool_calls_made.append(ToolCall(name=tool_name, input_parameters=tool_args, output=str(result)))

    # Step 4: send tool result back to the LLM
    messages.append(response.choices[0].message)
    messages.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id})

    # Step 5: LLM generates the final response
    final = await _client.chat.completions.create(model=_llm_model, messages=messages)
    return AgentResponse(output=final.choices[0].message.content, tools_called=tool_calls_made)
```

The `ToolCall` object is the key linkage: it records `name`, `input_parameters`, and `output` for each tool the agent actually called. This is what DeepEval's `LLMTestCase` expects in its `tools_called` field.

### DeepEval concepts: LLMTestCase with ToolCall

```python
from deepeval.test_case import LLMTestCase, ToolCall
from deepeval.metrics import TaskCompletionMetric, ToolCorrectnessMetric

# A happy-path test case: agent correctly checks order status
case = LLMTestCase(
    input="What's the status of my order #12345?",
    actual_output="Your order #12345 (WidgetPro 3000) has shipped and will arrive in about 2 days.",
    tools_called=[
        ToolCall(
            name="check_order_status",
            input_parameters={"order_id": "12345"},
            output='{"status": "shipped", "product": "WidgetPro 3000", "estimated_delivery": "2 days", "amount": 199.0}'
        )
    ]
)

task_metric = TaskCompletionMetric(
    task="Help customers with order status, refunds, and product questions",
    threshold=0.7,
    verbose_mode=True,
)
tool_metric = ToolCorrectnessMetric(threshold=0.7)
```

`TaskCompletionMetric` asks: "Given the task description and the final output, did the agent complete what the user asked?" It's an LLM judge — it scores 0.0 to 1.0 and reasons about its decision.

`ToolCorrectnessMetric` asks: "Were the tools actually called the right ones for this task?" It compares `tools_called` against what a correct agent *should* have called. If the agent answered without calling any tool, it scores low. If it called `process_refund` for a status check, it scores low.

Both metrics are threshold-based — `.measure(case)` returns a score, and the metric's `.is_successful()` checks against the threshold.

### Equivalence partitioning: tool selection (Module 4 Day 4 applied to a new axis)

Module 4 Day 4 introduced equivalence partitioning as a way to stop accidentally testing only the happy path. Same technique, new dimension — instead of partitioning by "number of hops required" (Module 6), we partition by "which tool selection the input demands":

```python
# Module 4 Day 4's technique, applied to tool selection
tool_selection_partitions = {
    "correct_tool_correct_args": "happy path — right tool, right input — order #12345 → check_order_status('12345')",
    "wrong_tool":                "process_refund called for a status check — same class of failure as Module 6's premature_stop",
    "no_tool_called":            "LLM answers from parametric memory instead of calling a tool — the Air Canada failure mode",
    "correct_tool_wrong_args":   "check_order_status called with '99999' when user asked about '12345' — Day 2's argument partition",
}
```

Without this partition, a test suite built from only `correct_tool_correct_args` cases will pass 100% and catch nothing. The hard negatives in `golden_dataset.json` are designed to exercise every cell.

> **Module 4 Day 4 connection — naming it explicitly:** in Day 4, you drew a grid of "partitions × metrics" and called out which cells had no test. That's the coverage matrix. The `wrong_tool` and `no_tool_called` partitions are the gaps that look fine until you add the Air Canada case — because neither can be caught by a metric that only looks at the final answer text.

### Hard negative: wrong tool called

The `order-status-01-hardneg` case in `golden_dataset.json` has the agent calling `process_refund` for a simple status check. This is a Tool Correctness failure — the task didn't need a refund, and initiating one would actively harm the customer. `ToolCorrectnessMetric` catches it because `tools_called` names the wrong function:

```python
wrong_tool_case = LLMTestCase(
    input="What's the status of my order #12345?",
    actual_output="I've processed a refund for order #12345.",
    tools_called=[
        ToolCall(
            name="process_refund",                   # WRONG — user asked for status, not refund
            input_parameters={"order_id": "12345", "reason": "status inquiry"},
            output='{"refund_id": "R-001", "amount": 199.0, "status": "initiated"}'
        )
    ]
)
# ToolCorrectnessMetric will score this low — process_refund is wrong for the stated task
```

### Hard negative: no tool called

The `product-info-01-hardneg` case has the agent answering a product question without calling `get_product_info` at all — the Air Canada pattern:

```python
no_tool_case = LLMTestCase(
    input="What's the cancellation fee for TurboMax Pro?",
    actual_output="The cancellation fee for TurboMax Pro is $25.",   # hallucinated — no tool called
    tools_called=[]                                                   # empty! no ToolCall records
)
# ToolCorrectnessMetric will score this low — the expected tool was never called
# TaskCompletionMetric may still score it high if the answer sounds plausible — this is why you need BOTH
```

This also illustrates why you need both metrics: `TaskCompletionMetric` alone may give a passing score because the answer *sounds* like a valid product inquiry answer. `ToolCorrectnessMetric` fails it regardless of how the output sounds.

### Demo you'll see
**`examples/01_deepeval_agent_metrics.ipynb`**

Exercise: [`exercises/01_deepeval_agent_metrics_exercise.md`](exercises/01_deepeval_agent_metrics_exercise.md)

### Key takeaways
1. Real tool-calling adds two new failure modes Module 6 couldn't see: wrong tool selected, and no tool called at all.
2. `ToolCorrectnessMetric` catches both — it inspects `tools_called`, not just the final output text.
3. Air Canada's chatbot failure was a "no tool called" failure at scale. Your hard negatives should include `tools_called=[]` cases.
4. Module 4 Day 4's equivalence partitioning still works — `tool_selection_partitions` is exactly that technique, one axis shifted.
5. Both `TaskCompletionMetric` and `ToolCorrectnessMetric` are needed: the first catches incomplete tasks, the second catches wrong-tool paths even when the answer sounds plausible.

---

## DAY 2 — ArgumentCorrectnessMetric + StepEfficiencyMetric + Coverage Matrix (60 min)

### Learning objectives
- Explain the distinction between wrong-tool failures (Day 1) and wrong-argument failures (Day 2)
- Build test cases that expose `ArgumentCorrectnessMetric` failures using cross-contamination bugs
- Apply `StepEfficiencyMetric` to detect agents that take too many tool calls to complete a simple task
- Close the coverage matrix started in Module 4 Day 4 and extended in Modules 5 and 6
- Retire Module 6's hand-rolled `MemoryRetentionVerdict` and `ReasoningChainVerdict` with confidence

### ArgumentCorrectnessMetric: right tool, wrong input

Day 1 caught the agent calling the wrong *function*. Day 2 catches the agent calling the right function with the wrong *arguments*. These are distinct failure modes and need distinct test cases.

The canonical example is **argument contamination**: a customer asks about order #12345, but somewhere in the conversation history there's a mention of order #67890 (a different customer's earlier query). The agent calls `check_order_status` (correct tool) but passes `order_id="67890"` (wrong argument — pulled from context instead of the current message).

```python
from deepeval.metrics import ArgumentCorrectnessMetric

argument_metric = ArgumentCorrectnessMetric(threshold=0.7, verbose_mode=True)

# Wrong argument case: right tool, wrong order_id
wrong_arg_case = LLMTestCase(
    input="Can you tell me the status of order #12345?",
    actual_output="Your order is currently being processed and will ship in 5 days.",
    tools_called=[
        ToolCall(
            name="check_order_status",       # CORRECT tool
            input_parameters={"order_id": "67890"},  # WRONG argument — contaminated from context
            output='{"status": "processing", "product": "TurboMax Pro", "estimated_delivery": "5 days", "amount": 299.0}'
        )
    ]
)
# ArgumentCorrectnessMetric will score this low — the tool was right but the argument was wrong
# Note: the output sounds plausible because order 67890 is a real processing order — this is the insidious version
```

> **Connection to Module 6's MemoryRetentionVerdict:** Module 6's `MemoryRetentionVerdict` checked whether an early-hop fact survived correctly into the final answer. This is the same failure at a different layer — instead of a fact from hop 1 corrupting the final answer, a value from a prior conversation turn corrupts the argument to the current tool call. Same cross-contamination family, different mechanism.

> **Connection to Module 4 Day 4 BVA:** Boundary-value analysis in Day 4 tested what happens at the edges of valid input ranges. `order_id` is a categorical boundary — there's a boundary between "the order_id in the current user message" and "order_ids that appeared anywhere else in the context." The bug lives right at that boundary.

### StepEfficiencyMetric: too many tool calls for the task

A correct agent should complete a status check in one tool call: `check_order_status`. An inefficient agent might call `check_order_status`, then `get_product_info` on the order's product, then `escalate_to_human` "just to be safe" — three calls when one was enough.

`StepEfficiencyMetric` scores this. It compares the number of tool calls actually made against the expected minimum, and penalizes padding:

```python
from deepeval.metrics import StepEfficiencyMetric

efficiency_metric = StepEfficiencyMetric(threshold=0.7, verbose_mode=True)

# Inefficient case: escalation that triggered 3 tool calls when 1 was needed
inefficient_case = LLMTestCase(
    input="I have a complaint about my recent experience.",
    actual_output="I've escalated your complaint to our team. Your ticket is CS-9001.",
    tools_called=[
        ToolCall(name="check_order_status",  input_parameters={"order_id": "unknown"}, output='{"error": "Order not found"}'),
        ToolCall(name="get_product_info",    input_parameters={"product_name": "unknown"}, output='{"error": "Product not found"}'),
        ToolCall(name="escalate_to_human",   input_parameters={"reason": "general complaint"}, output='{"ticket_id": "CS-9001", "estimated_wait": "2 hours", "queue": "general"}'),
    ]
)
# StepEfficiencyMetric will score this low — escalate_to_human alone was sufficient
```

> **Connection to Module 6's ReasoningChainVerdict:** Module 6's `ReasoningChainVerdict` checked whether the agent's reasoning chain was valid end-to-end. `StepEfficiencyMetric` is a tighter version: it doesn't just ask "was the chain valid?" — it asks "was it the *shortest valid* chain?" An agent that always takes 5 steps where 2 would do is not wrong, but it's expensive, slow, and likely looping unnecessarily.

> **Connection to Module 6's infinite-retrieval-loop failure:** Module 6 Day 1 defined "infinite retrieval loop" as the planner that never decides it has enough information. `StepEfficiencyMetric` is the tool-calling analog: an agent that keeps calling tools past the point of sufficiency. It's bounded (can't actually be infinite in a real system with a max-turns limit), but the metric catches the pathological tendency before it becomes a production cost problem.

### Combined run: all four metrics

By Day 2, you have four metrics and a complete picture of an agent's health:

```python
from deepeval import evaluate
from deepeval.test_case import LLMTestCase, ToolCall
from deepeval.metrics import (
    TaskCompletionMetric,
    ToolCorrectnessMetric,
    ArgumentCorrectnessMetric,
    StepEfficiencyMetric,
)

task_metric      = TaskCompletionMetric(task="...", threshold=0.7)
tool_metric      = ToolCorrectnessMetric(threshold=0.7)
argument_metric  = ArgumentCorrectnessMetric(threshold=0.7)
efficiency_metric = StepEfficiencyMetric(threshold=0.7)

evaluate(
    test_cases=all_cases,
    metrics=[task_metric, tool_metric, argument_metric, efficiency_metric],
)
```

Each case from `golden_dataset.json` exercises the metric most sensitive to its failure mode. The happy-path cases exercise all four (they should all pass). The hard negatives are designed so that one specific metric will fail while the others may still pass — that's what makes them *hard* negatives, not just obviously wrong answers.

### Coverage matrix: complete and closed

Module 4 Day 4 introduced the coverage matrix. Module 5 extended it with retrieval columns. Module 6 added agentic columns. Today's version is the full accumulated matrix, incorporating everything:

| Capability ↓ / Failure mode → | hallucination | wrong_tool | wrong_argument | inefficient_steps | ungraceful_failure |
|---|---|---|---|---|---|
| `order_management` | covered (`task_metric`) | covered (`order-status-01-hardneg`) | covered (`refund-01-hardneg`) | covered (`escalation-01-hardneg`) | covered (`task_metric`) |
| `product_inquiry`  | covered (`task_metric`) | covered (`product-info-01-hardneg`) | covered (Day 2 extension) | covered (Day 2 extension) | covered (`task_metric`) |
| `refund_processing` | covered (`task_metric`) | covered (golden_dataset) | covered (`refund-01-hardneg`) | covered (golden_dataset) | covered (`task_metric`) |

Notice the pattern: every row has a hard negative for `wrong_tool` and `wrong_argument`. This isn't accidental — Module 4 Day 4's coverage matrix discipline means you write hard negatives to fill gaps, not just to cover happy paths.

> **Why the matrix matters here:** without explicitly maintaining this table, you end up with a suite that tests `order_management` thoroughly (it's the first capability you built) and `refund_processing` lightly (it was added later). The matrix makes the gap visible. This is the same observation from Module 4 Day 4 — "the coverage matrix is the thing that tells you what you *haven't* tested yet."

### Running hard negatives from golden_dataset.json

The `golden_dataset.json` hard negatives can be loaded and run directly:

```python
import json
from deepeval.test_case import LLMTestCase, ToolCall

with open("golden_dataset.json") as f:
    dataset = json.load(f)

hard_negatives = [d for d in dataset if d["is_hard_negative"]]

def dataset_entry_to_test_case(entry: dict) -> LLMTestCase:
    tools_called = [
        ToolCall(
            name=tc["name"],
            input_parameters=tc["input_parameters"],
            output=str(tc["output"]),
        )
        for tc in entry.get("tools_called", [])
    ]
    return LLMTestCase(
        input=entry["user_input"],
        actual_output=entry["response"],
        tools_called=tools_called,
    )

hard_negative_cases = [dataset_entry_to_test_case(e) for e in hard_negatives]

# Each hard negative should fail its target metric and pass the others
evaluate(test_cases=hard_negative_cases, metrics=[task_metric, tool_metric, argument_metric, efficiency_metric])
```

The `eval_type` field in each golden dataset entry tells you which metric should flag it:
- `"tool_correctness"` → `ToolCorrectnessMetric` should fail
- `"argument_correctness"` → `ArgumentCorrectnessMetric` should fail
- `"step_efficiency"` → `StepEfficiencyMetric` should fail
- `"task_completion"` → `TaskCompletionMetric` should fail

If a metric *doesn't* fail on its designated hard negative, that's a signal about metric calibration, not a passing test.

### Retiring Module 6's hand-rolled judges

At this point, you can stop importing from Module 6's judge functions:

| What you used in Module 6 | Why it was necessary | Why you can retire it now |
|---|---|---|
| `MemoryRetentionVerdict` | `must_include` string checking | `ArgumentCorrectnessMetric` — LLM-judged, threshold-able, no string matching |
| `ReasoningChainVerdict` | `must_not_include` string checking | `ToolCorrectnessMetric` — checks the tool call record, not the output string |
| `GracefulFailureVerdict` | hedge-phrase list checking | `TaskCompletionMetric` — asks "was the task completed?" which includes graceful admission of inability |

The hand-rolled versions were correct but brittle — a slight phrasing change in the agent's output could bypass string matching. The DeepEval metrics are LLM-judged and robust to surface wording variation.

### Demo you'll see
**`examples/02_step_argument_efficiency.ipynb`**

Exercise: [`exercises/02_step_argument_efficiency_exercise.md`](exercises/02_step_argument_efficiency_exercise.md)

### Key takeaways
1. Wrong argument is a distinct failure from wrong tool — `ArgumentCorrectnessMetric` catches right-tool-wrong-input bugs that `ToolCorrectnessMetric` would pass.
2. Argument contamination from context history is the tool-calling analog of Module 6's memory-retention failure — same cross-contamination, different layer.
3. `StepEfficiencyMetric` is the tool-calling analog of Module 6's infinite-retrieval-loop — excessive tool calls are caught before they become a production cost problem.
4. The coverage matrix is now three modules wide. Every new capability you add should extend it, not replace it.
5. Module 6's hand-rolled verdict functions are fully retired — the DeepEval equivalents are more robust and don't need to be rewritten per agent.

---

## Module 7 → Module 8 bridge

You now have a complete, formal test suite for a tool-calling agent: task completion, tool correctness, argument correctness, and step efficiency — all expressed as `LLMTestCase` objects that can be run in a loop, scored against thresholds, and reported in the DeepEval dashboard. The coverage matrix spans four modules and every cell has at least one test.

Module 8 turns this foundation adversarial. Instead of testing whether your agent behaves correctly under normal use, you'll probe whether it can be *made to misbehave* by a user who is deliberately trying to break it — prompt injection, jailbreaks, social engineering to bypass tool restrictions. The same `LLMTestCase` format carries over; what changes is the source of the `input` field (crafted adversarial probes, not realistic user queries) and the metric family (DeepEval's red-teaming metrics, not completion/correctness metrics).

---

## Plain-English Glossary

| Term | Technical | Plain English |
|---|---|---|
| **Tool-calling agent** | An LLM that selects and invokes named functions via the OpenAI tools API | A customer service rep who can actually look things up and take actions, not just chat |
| **ToolCall record** | `deepeval.test_case.ToolCall` — name, input_parameters, output | A receipt: which tool ran, what it was given, what it returned |
| **TaskCompletionMetric** | LLM judge scoring whether the agent completed the user's stated task | Did the rep actually solve the customer's problem? |
| **ToolCorrectnessMetric** | LLM judge scoring whether the right tools were called | Did the rep use the right system, or click through random menus? |
| **ArgumentCorrectnessMetric** | LLM judge scoring whether the arguments passed to tools were correct | Did the rep look up the right customer's account, or accidentally pull up someone else's? |
| **StepEfficiencyMetric** | LLM judge scoring whether the agent completed the task in a reasonable number of tool calls | Did the rep resolve it in one step, or bounce the customer through three departments first? |
| **Argument contamination** | Agent passes an argument value from a previous context turn instead of the current one | Writing down last week's customer's order number instead of this week's |
| **Tool bypass** | Agent answers a question from parametric memory without calling the relevant tool | Telling a customer their balance from memory instead of looking it up — and being wrong |
| **Coverage matrix** | A grid mapping capabilities against failure modes, showing which combinations have test cases | The QA team's gap-analysis spreadsheet, made precise |
| **Hard negative** | A test case designed to look almost correct but fail on a specific metric | A trick question for your test suite — if it passes a hard negative, the metric is not working |
