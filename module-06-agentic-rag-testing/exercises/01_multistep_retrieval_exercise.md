# Exercise: Multi-Step Retrieval & Planner/Executor Flows

**Estimated time:** 35–45 minutes

---

## Part A — Break the Loop on Purpose (15 min)

Using `agentic_rag()` from the Day 1 notebook:

1. **Premature stop:** change `has_enough_info()` to return `True` the moment *any* fact is retrieved, regardless of content. Run the loop on the WidgetPro question. What wrong answer comes out, and why does it look superficially plausible rather than obviously broken?
2. **Infinite loop:** change the reformulation logic so `query` never changes between hops. Run with `max_hops=3`. What does the loop actually do when it exhausts `max_hops` without `has_enough_info()` ever returning `True`? Is silently returning the wrong answer better or worse than raising an error — justify your answer.
3. **Query drift:** write a reformulation rule that, on hop 2, asks a question only tangentially related to the original (e.g. drifts from "cancellation fee" to "release date"). What does the resulting trace look like, and how would you describe this bug to someone who's only looking at the final answer, not the trace?

---

## Part B — A 3-Hop Question of Your Own (15 min)

Design a question that genuinely requires 3 hops to answer (not 2, not 1) — pick any domain you like. For example: "What's the warranty period for the successor of the product that replaced the original WidgetPro?"

1. Build the `KNOWLEDGE_BASE` entries needed for all 3 hops.
2. Update `retrieve()` so each hop returns the correct fact deterministically (same style as the Day 1 example — distinctive keywords routing to distinctive facts).
3. Update `has_enough_info()` so the loop doesn't stop early.
4. Run it and confirm the trace shows exactly 3 `retriever` spans.

---

## Part C — Equivalence Partition Review (10 min)

Take 3 real questions a system in your domain (or a domain you're familiar with) might receive. Classify each into `single_hop`, `two_hop`, or `three_plus_hop` using the Day 1 partition. For the one you found hardest to classify, write one sentence on what made the hop count ambiguous.

---

## Self-Check

- [ ] You triggered all 3 named bugs (premature stop, infinite loop, query drift) on purpose, not by accident
- [ ] Your 3-hop question actually takes exactly 3 hops when run, not 2 or 4
- [ ] You can explain, without re-reading the notes, why none of these 3 bugs could happen in Module 5's single-pass pipeline
- [ ] You classified at least one real-world question as ambiguous between hop counts and can say why
