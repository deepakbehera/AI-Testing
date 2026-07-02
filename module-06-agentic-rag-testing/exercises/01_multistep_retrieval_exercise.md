# Exercise: Multi-Step Retrieval & Planner/Executor Flows

**Estimated time:** 35–45 minutes
**Setup:** `../examples/.env` must be configured (copy `../.env.example` and fill in your deployed LLM's credentials) — every part below calls the real `agentic_rag()` from `../examples/agent.py`.

---

## Part A — Probe the Loop's Real Behavior (15 min)

Unlike a rule-based stand-in, you can't just flip a boolean to force a specific bug here — the planner is a live LLM. That's the point: probing a real agent means constructing inputs that make a failure *likely*, then checking whether it actually happened.

1. **Premature stop:** call `await agentic_rag(question, max_hops=1, verbose=True)` on the WidgetPro question from the Day 1 notebook. What incomplete or wrong answer comes out? Does the generator hedge about the missing hop, or guess anyway?
2. **Hop exhaustion:** ask a question the corpus cannot answer at all (e.g. `"What is the CEO's phone number?"`) with the default `max_hops=3` and `verbose=True`. Does the planner ever set `enough_info=True`? Check `result.hit_max_hops` — it should be `True`. Read the generator's answer: does it hedge because it was told the planner was uncertain (see `_generate`'s `uncertain` parameter in `agent.py`), or does it guess anyway? Is silently generating an answer from whatever partial facts exist — even a hedged one — better or worse than raising an error instead? Justify your answer.
3. **Query drift, applied by hand:** `retrieve()` is `async` and importable on its own — call `await retrieve("release date")` (or any query deliberately unrelated to a question you care about) directly in a notebook cell. What comes back? Now imagine the planner's real `next_query` had drifted this way on hop 2 of a genuine run — what would the final answer likely look like, and how would you notice from the trace alone?

---

## Part B — A 3-Hop Question of Your Own (15 min)

Design a question that genuinely requires 3 hops to answer (not 2, not 1) — pick any domain you like. For example: "What's the current price of the product that replaced the product that replaced the original WidgetPro?"

1. Add the facts needed for all 3 hops to `CORPUS` in `../examples/agent.py`.
2. Ask your question with `verbose=True` and `max_hops=4` (give the real planner headroom to actually need all 3 hops).
3. Does it correctly take 3 hops (`hit_max_hops=False`)? If it stops early or never stops (`hit_max_hops=True`), is the bug in your corpus design (a shortcut path exists) or a genuine planner limitation — how would you tell the difference by reading the printed `reasoning` at each hop?

---

## Part C — Equivalence Partition Review (10 min)

Take 3 real questions a system in your domain (or a domain you're familiar with) might receive. Classify each into `single_hop`, `two_hop`, or `three_plus_hop` using the Day 1 partition. For the one you found hardest to classify, write one sentence on what made the hop count ambiguous.

---

## Self-Check

- [ ] You ran all 3 probes in Part A against the real agent and can describe what actually happened, not what you expected to happen
- [ ] Your 3-hop question actually takes exactly 3 hops when run, not 2 or 4 — or you can explain why not
- [ ] You can explain, without re-reading the notes, why none of these failure shapes could happen in Module 5's single-pass pipeline
- [ ] You classified at least one real-world question as ambiguous between hop counts and can say why
