# Module 6 — Agentic RAG Testing

**Duration:** 2 hours · split across **2 online sessions of 1 hour each**
**Prerequisites:** Module 4 (DeepEval, golden datasets, **the testing mindset — Day 4**) · Module 5 (RAGAS, the retriever/generator split, LangSmith tracing)

Module 5 tested a system that retrieves **once**, then generates **once**. Real systems are rarely that simple — a planner decides whether it has enough information, reformulates the query if not, and may retrieve several times before answering. That's agentic RAG. The testing mindset doesn't change; the system under test gets one more moving part, and that part needs its own failure-mode vocabulary.

---

## How the 2 sessions are organized

| Day | Focus | What you'll build |
|---|---|---|
| **1** | Multi-step retrieval & planner/executor flows | A traced 2-hop agentic loop, with the new failure modes that only exist in multi-step retrieval |
| **2** | Tool/memory validation, multi-hop reasoning & failure-path testing | Hard negatives for "right facts, wrong combination" and graceful failure when a hop comes up empty |

---

## DAY 1 — Multi-Step Retrieval & Planner/Executor Flows (60 min)

### Learning objectives
- Explain how agentic RAG differs from Module 5's single retrieve-then-generate flow
- Name the failure modes that only exist once retrieval can happen more than once
- Build a minimal planner/executor loop and trace every hop with LangSmith
- Apply equivalence partitioning (Module 4 Day 4) to "number of hops required" as a new dimension

### From one retrieval to many

Module 5's flow was a straight line:

```
User question -> RETRIEVER -> GENERATOR -> answer
```

Agentic RAG adds a decision point that can loop:

```
User question
    │
    ▼
PLANNER  →  do I have enough information to answer? if not, what should I search for next?
    │
    ├─ NOT ENOUGH  →  reformulate query  →  RETRIEVER  →  back to PLANNER
    │
    └─ ENOUGH      →  GENERATOR  →  final answer
```

> **Plain English:** Module 5's system was a librarian who fetches one book and writes a summary. An agentic RAG system is a research assistant who reads the first book, realizes it raises a follow-up question, goes back for a second book, and only writes the summary once they actually have what they need. The second assistant is more capable — and has far more ways to go wrong before they ever start writing.

### Real incident: Klarna's AI customer service rollback (May 2025)

Klarna replaced roughly 700 customer-service roles with an OpenAI-powered AI assistant, reporting in early 2024 that it handled two-thirds of chats with under-2-minute resolution times. By May 2025, CEO Sebastian Siemiatkowski publicly walked the rollout back and resumed hiring human agents. The detail that matters for this module: **AI matched human performance on simple queries** (order status, payment schedules) **but quality dropped noticeably on complex cases** — disputes, fraud claims, hardship cases — exactly the questions that require chaining several pieces of information together rather than answering from one lookup.

> **Why this matters for today:** "simple query" is a Module 5 problem — one retrieval, one answer. "Complex dispute" is a Module 6 problem — it needs the planner to recognize that one retrieved fact isn't enough, go fetch more, and reason across all of it. Klarna's gap between the two is the exact gap this module is about testing for *before* a rollout, not after.

### New failure modes that only exist in multi-step retrieval

| Failure mode | What it looks like |
|---|---|
| **Infinite retrieval loop** | The planner never decides it has enough information; it keeps reformulating and re-querying |
| **Premature stop** | The planner answers after 1 hop when the question genuinely needed 2-3 |
| **Query drift** | Each reformulated query moves further from the user's actual intent |
| **Reasoning chain break** | Every needed fact was retrieved correctly across hops, but combined incorrectly at the end (Day 2 builds this one) |

None of these can happen in Module 5's single-pass flow — they only exist because the system can now make a *decision* about whether to continue.

### Equivalence partitioning: hops required

Same technique from Module 4 Day 4, new dimension:

```python
hop_partitions = {
    "hops_required": {
        "single_hop":   "the answer is fully contained in one retrievable chunk",
        "two_hop":      "the answer requires combining facts from two separate retrievals",
        "three_plus_hop": "the answer requires chaining three or more retrievals",
    },
}
```

A test suite built only from `single_hop` cases will pass beautifully and tell you nothing about whether your planner can handle a Klarna-style dispute — the same "happy path only" trap from Module 4 Day 4, one layer up.

### Building and tracing a 2-hop loop

```python
from langsmith import traceable

# A small knowledge base where the answer requires TWO hops:
# "What is the cancellation fee for the product that replaced WidgetPro 2000?"
KNOWLEDGE_BASE = {
    "discontinuation": "WidgetPro 2000 was discontinued in 2023 and replaced by WidgetPro 3000.",
    "fee_3000":        "WidgetPro 3000's cancellation fee is $0 — it can be canceled anytime at no charge.",
    "fee_2000":        "WidgetPro 2000's cancellation fee was $50 before it was discontinued.",
}

@traceable(run_type="retriever")
def retrieve(query: str) -> list[str]:
    # A deliberately simple, deterministic stand-in retriever — real systems use
    # embedding similarity (Module 5 Day 2). Keeping it rule-based here makes the
    # PLANNER's looping behavior the thing under test, not the retriever's ranking.
    q = query.lower()
    if "3000" in q:
        return [KNOWLEDGE_BASE["fee_3000"]]
    if "replaced" in q or "discontinued" in q:
        return [KNOWLEDGE_BASE["discontinuation"]]
    return [KNOWLEDGE_BASE["fee_2000"]]

@traceable(run_type="chain", name="planner")
def has_enough_info(question: str, facts_so_far: list[str]) -> bool:
    # Rule-based stand-in for an LLM planner: "enough" once we have a fee figure.
    return any("fee is" in f or "fee was" in f for f in facts_so_far)

@traceable(run_type="chain", name="agentic_rag_loop")
def agentic_rag(question: str, max_hops: int = 3) -> tuple[str, list[str]]:
    facts: list[str] = []
    query = question
    for hop in range(1, max_hops + 1):
        new_facts = retrieve(query)
        facts.extend(new_facts)
        if has_enough_info(question, facts):
            break
        # Reformulate: once we know the replacement product, search for ITS fee.
        query = "WidgetPro 3000 cancellation fee" if hop == 1 else question
    return f"[{hop} hop(s)] facts used: {facts}", facts

answer, facts = agentic_rag("What is the cancellation fee for the product that replaced WidgetPro 2000?")
print(answer)
```

With `LANGSMITH_TRACING` enabled, this shows up as a single `agentic_rag_loop` trace with nested `retriever` and `planner` spans per hop — exactly the trace tree you'd inspect to tell whether a real failure was premature stopping (planner span returns `True` too early) or query drift (the reformulated query in the second `retriever` span has wandered off-topic).

### Demo you'll see
**`examples/01_multistep_retrieval.ipynb`**

Exercise: [`exercises/01_multistep_retrieval_exercise.md`](exercises/01_multistep_retrieval_exercise.md)

### Key takeaways
1. Agentic RAG adds exactly one new component — a planner that decides whether to continue — and that decision point is where all of today's new failure modes live.
2. Klarna's real "simple vs. complex" quality gap is the single-hop vs. multi-hop gap, made concrete.
3. Equivalence partitioning by `hops_required` is what stops a test suite from being accidentally all single-hop.
4. Tracing a multi-hop chain isn't optional here the way it was a nice-to-have in Module 5 — without per-hop spans, you genuinely cannot tell premature stopping from query drift from a clean 2-hop success.

---

## DAY 2 — Tool/Memory Validation, Multi-Hop Reasoning & Failure-Path Testing (60 min)

### Learning objectives
- Validate that facts retrieved in an early hop are still correctly available at the final answer (memory/context validation)
- Build a multi-hop hard negative: the "right facts, wrong combination" failure
- Test graceful failure when a hop returns nothing relevant
- Extend the coverage matrix from Module 5 Day 2 with agentic-specific failure-mode columns

### Memory validation: did the early fact survive?

A 3-hop chain passes 2 facts forward into a final generation step. Module 4 Day 4 taught you to boundary-test a context window; this is the same boundary, relocated: **does the fact from hop 1 still make it into the final answer, or does it get dropped or corrupted by hop 3?**

```python
def facts_present_in_answer(answer: str, required_facts: list[str]) -> dict:
    missing = [f for f in required_facts if f not in answer]
    return {"missing": missing, "passed": len(missing) == 0}

required = ["WidgetPro 3000"]  # the hop-1 conclusion that must survive into the final answer

answer_with_memory = "WidgetPro 3000's cancellation fee is $0, since it replaced WidgetPro 2000 in 2023."
answer_memory_dropped = "The cancellation fee is $0."  # hop 1's product identity got truncated away

for label, answer in [("MEMORY INTACT", answer_with_memory), ("MEMORY DROPPED", answer_memory_dropped)]:
    print(f"[{label}] -> {facts_present_in_answer(answer, required)}")
```

> **Plain English:** this is the chunk-boundary bug from Module 5 Day 2, except the "chunk" is the running memory of a multi-hop conversation instead of a document. The boundary is wherever your agent truncates history — and it can split a needed fact out exactly the same way a 500-token chunk boundary could.

### Hard negative — right facts, wrong combination (`reasoning_chain_break`)

This is the failure mode Module 5's single-hop metrics structurally cannot catch, because both retrieved facts are individually faithful to their source — the bug is in how they were *combined*.

```python
hop1_fact = "WidgetPro 2000 was discontinued in 2023 and replaced by WidgetPro 3000."
hop2_facts = [
    "WidgetPro 3000's cancellation fee is $0.",
    "WidgetPro 2000's cancellation fee was $50.",
]

# Hard negative: the agent answers with the OLD product's fee instead of the new one's —
# every individual fact is true and grounded; the combination is wrong.
reasoning_break_answer = "The cancellation fee for the product that replaced WidgetPro 2000 is $50."
correct_answer = "The cancellation fee for the product that replaced WidgetPro 2000 (WidgetPro 3000) is $0."

def check_correct_product_fee(answer: str) -> bool:
    # The question asks about the REPLACEMENT product — the answer must cite WidgetPro 3000's fee, not 2000's.
    return "$0" in answer and "WidgetPro 3000" in answer

for label, answer in [("HARD NEGATIVE (should fail)", reasoning_break_answer), ("CORRECT (should pass)", correct_answer)]:
    print(f"[{label}] -> passed={check_correct_product_fee(answer)}")
```

> A faithfulness check alone would pass the hard negative above — `$50` really is in the retrieved context. This is exactly why agentic RAG needs reasoning-level checks on top of Module 5's faithfulness/groundedness checks, not instead of them.

### Failure-path testing: the hop that comes up empty

What should the agent do when hop 2 finds nothing relevant? Two outcomes:

- **Graceful** — "I found that WidgetPro 3000 replaced WidgetPro 2000, but I don't have its cancellation fee on file."
- **Ungraceful** — confidently invents a fee number to fill the gap.

```python
def empty_hop_response_is_graceful(response: str) -> bool:
    hedge_phrases = ["don't have", "couldn't find", "no information", "not available"]
    return any(phrase in response.lower() for phrase in hedge_phrases)

graceful   = "I found that WidgetPro 3000 replaced WidgetPro 2000, but I don't have its cancellation fee on file."
ungraceful = "The cancellation fee for WidgetPro 3000 is $25."   # invented — hop 2 found nothing

print(f"graceful   -> {empty_hop_response_is_graceful(graceful)}")
print(f"ungraceful -> {empty_hop_response_is_graceful(ungraceful)}")
```

This is a hard negative aimed squarely at the failure pattern behind Klarna's "complex cases dropped in quality" — an agent that can't find the next fact should say so, not fabricate one to keep the chain moving.

### Extending the coverage matrix

Module 5 Day 2 added retrieval columns to Module 4 Day 4's matrix. Today adds the agentic ones:

| Capability ↓ / Failure mode → | hallucination | reasoning_chain_break | premature_stop | ungraceful_failure |
|---|---|---|---|---|
| `single_hop_qa` | covered (Module 5) | n/a | n/a | 0 |
| `multi_hop_qa` | 0 | covered (today) | 0 ← gap | covered (today) |

The `single_hop_qa` row not needing the agentic columns is itself useful information — it tells you those columns only matter once a capability genuinely requires multiple hops.

### Demo you'll see
**`examples/02_tool_memory_reasoning.ipynb`**

Exercise: [`exercises/02_tool_memory_reasoning_exercise.md`](exercises/02_tool_memory_reasoning_exercise.md)

### Key takeaways
1. Memory/context validation across hops is a boundary-value problem, same family as Module 5's chunk-boundary bug.
2. `reasoning_chain_break` is invisible to per-fact faithfulness checks — it requires a check that looks at how facts were *combined*, not just whether each one is grounded.
3. Graceful failure on an empty hop is a testable, hard-negative-able behavior, not a hope.
4. The coverage matrix keeps growing the same way it has since Module 4 Day 4 — new columns, same matrix, same habit.

---

## Module 6 → Module 7 bridge

You can now build and trace a multi-hop retrieval loop and catch the failure modes specific to it by hand: reasoning-chain breaks, premature stops, ungraceful failures. Module 7 formalizes exactly these checks into DeepEval's purpose-built agent metrics — task completion, tool correctness, argument correctness, turn relevancy — so you stop hand-rolling `check_correct_product_fee()`-style functions and get a proper, reusable framework for it. The agent in Module 7 also gains real tool-calling (not just retrieval), which is where today's "tool validation" groundwork starts paying off.

---

## Plain-English Glossary

| Term | Technical | Plain English |
|---|---|---|
| **Agentic RAG** | RAG with a planning loop that can retrieve more than once | A research assistant who goes back for a second book when the first wasn't enough |
| **Planner** | The component deciding whether to retrieve again or answer now | The assistant's internal "do I know enough yet?" check |
| **Hop** | One retrieve-and-evaluate cycle within the loop | One trip to the library |
| **Multi-hop reasoning** | Combining facts from more than one retrieval to answer | Connecting clue A from chapter 1 to clue B from chapter 5 |
| **Infinite retrieval loop** | The planner never decides it has enough information | The assistant who keeps going back to the library and never starts writing |
| **Premature stop** | Answering after too few hops | Writing the report after reading only the first page |
| **Query drift** | Reformulated queries wandering away from the original intent | A game of telephone, applied to search queries |
| **Reasoning chain break** | Correct facts, combined incorrectly | Citing the right two sources but drawing the wrong conclusion from them |
| **Ungraceful failure** | Inventing an answer instead of admitting a gap in retrieved information | Confidently making up the ending of a book you didn't finish |
