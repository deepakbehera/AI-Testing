# Module 6 — Resources: Agentic RAG Testing

---

## Carrying Forward From Modules 4-5

- Module 4 `examples/04_testing_mindset.ipynb` — equivalence partitioning, boundary value analysis, the coverage matrix, hard negatives. Every technique this module uses is from here, pointed at a new layer (the planner loop).
- Module 5 `examples/03_groundedness_pipeline.ipynb` — the `@traceable` LangSmith pattern and the "score is the alarm, trace is the investigation" framing, now extended to a multi-span chain.
- Module 5 `notes.md`, Day 2 — the chunk-boundary bug; this module's memory-validation problem is the same boundary relocated to conversation memory.

---

## Real-World Incident Referenced in This Module

- [CX Dive — Klarna reinvests in human talent for customer service](https://www.customerexperiencedive.com/news/klarna-reinvests-human-talent-customer-service-AI-chatbot/747586/) — May 2025 reporting on Klarna's reversal; confirms AI matched humans on simple queries but quality dropped on complex, multi-step cases (disputes, fraud, hardship), and that the AI sometimes gave "confident-but-wrong answers about policy, fees, or payment terms" — used as this module's anchor incident

---

## Agentic / Multi-Step RAG Architecture

- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) — the foundational paper behind "plan, act, observe, repeat" loops used by most agentic RAG systems
- [Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection](https://arxiv.org/abs/2310.11511) — a model that decides for itself when to retrieve, directly relevant to the planner's "do I have enough information?" decision
- [LangGraph Overview](https://docs.langchain.com/oss/python/langgraph/overview) — a common framework for building the planner/executor loops this module tests (used conceptually here; the notebooks use a rule-based stand-in to keep examples dependency-light)

---

## Multi-Hop Question Answering Benchmarks

- [HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering](https://arxiv.org/abs/1809.09600) — the standard academic benchmark for exactly the 2-hop WidgetPro-style questions built in this module
- [MuSiQue: Multihop Questions via Single-hop Question Composition](https://arxiv.org/abs/2108.00573) — multi-hop questions explicitly constructed by composing single-hop questions, useful as a template for writing your own multi-hop test cases

---

## Tracing Multi-Step Pipelines (continuity from Module 5 Day 3)

- [LangSmith Observability Docs](https://docs.langchain.com/langsmith) — tracing setup
- [LangSmith Observability Quickstart](https://docs.langchain.com/langsmith/observability-quickstart) — the `@traceable` decorator pattern, with nested spans for multi-step chains

---

## Bridge to Module 7

- [DeepEval — Metrics Introduction](https://deepeval.com/docs/metrics-introduction) — covers the 6 agentic metrics (Task Completion, Argument Correctness, Tool Correctness, Step Efficiency, Plan Adherence, Plan Quality) that formalize the hand-rolled checks built in this module's Day 2
