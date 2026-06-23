# Module 5 — Resources: RAG Testing with RAGAS

---

## Official Documentation

- [RAGAS Documentation](https://docs.ragas.io) — full API reference, metric guides
- [RAGAS GitHub Repository](https://github.com/explodinggradients/ragas) — source, examples, changelog
- [RAGAS Core Concepts](https://docs.ragas.io/en/stable/concepts/) — metrics, testsets, and the evaluation dataset format

---

## The Paper Behind the Library

- [RAGAS: Automated Evaluation of Retrieval Augmented Generation](https://arxiv.org/abs/2309.15217) — introduces faithfulness, context precision/recall, and answer relevancy as automatically computable metrics without human-labeled references for every metric

---

## Carrying the Testing Mindset Forward (continuity from Module 4 Day 4)

- Module 4 `examples/04_testing_mindset.ipynb` — equivalence partitioning, boundary value analysis, the coverage matrix, and hard negatives. Every technique in that notebook applies directly to RAGAS test-set design; this module just adds retrieval-specific columns to the same matrix.
- Module 3 `notes.md`, Day 3, "RAG corpus poisoning" — the real example used as the anchor for this module's adversarial retrieval testing (Section on corpus poisoning / OWASP LLM08).

---

## Chunking & Retrieval

- [Pinecone — Chunking Strategies for LLM Applications](https://www.pinecone.io/learn/chunking-strategies/) — practical guide to fixed-size, recursive, semantic, and contextual chunking, with guidance on picking a strategy
- [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172) — why retrieval position matters, not just retrieval presence

---

## Tracing with LangSmith (Day 3)

- [LangSmith Observability Docs](https://docs.langchain.com/langsmith) — tracing setup, trace investigation, performance monitoring
- [LangSmith Observability Quickstart](https://docs.langchain.com/langsmith/observability-quickstart) — the `@traceable` decorator pattern used in Day 3's pipeline
- [LangSmith](https://smith.langchain.com) — sign up here; free tier is enough for this module's exercises

---

## Embeddings & Vector Databases

- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings) — embedding model selection and similarity scoring
- [MTEB: Massive Text Embedding Benchmark](https://arxiv.org/abs/2210.07316) — how embedding models are benchmarked; useful for choosing/validating an embedding model
- [Chroma](https://www.trychroma.com) and [FAISS](https://github.com/facebookresearch/faiss) — the two lightest-weight vector stores for local experimentation (Module 6 introduces a persistent vector DB in more depth)

---

## Groundedness & Faithfulness

- [TruthfulQA](https://arxiv.org/abs/2109.07958) — benchmark for measuring whether a model sticks to verifiable facts, conceptually adjacent to RAGAS faithfulness
- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) — the original RAG paper; useful background for *why* groundedness is the central RAG quality question

---

## RAGAS vs DeepEval

- [DeepEval — RAG Metrics](https://docs.confident-ai.com/docs/metrics-faithfulness) — DeepEval's own faithfulness/contextual metrics, useful for a side-by-side comparison with RAGAS's versions (Day 3)
- Module 4 `notes.md`, Day 2 — `FaithfulnessMetric` and `HallucinationMetric`; Day 3's worked real incident (Air Canada) is the same failure class RAGAS's `Faithfulness` metric targets, just measured with a different library

---

## Real-World RAG Failures Referenced in This Module

- Reporting on **Cursor's AI support agent inventing a subscription policy** (April 2025) — widely covered (TechCrunch, Ars Technica, The Register); used as this module's anchor incident for groundedness testing
- Module 3 `notes.md`, Day 3 — the Confluence-wiki RAG corpus-poisoning example, reused here as the basis for an adversarial retrieval test case
