# Exercise: RAGAS Fundamentals

**Estimated time:** 35–45 minutes

---

## Part A — Setup (10 min)

1. Install this module's dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and configure either Ollama (`ollama pull llama3.2:3b` and `ollama pull nomic-embed-text`) or `OPENAI_API_KEY`.
3. Run the setup cell from `examples/01_ragas_intro.ipynb` and confirm `judge_llm` and `judge_embeddings` print as ready.

---

## Part B — Retriever vs. Generator Failures (10 min)

For each scenario below, decide: is this most likely a **retriever** failure, a **generator** failure, or could be either? Justify each in one sentence.

1. A RAG support bot answers a question about a feature that doesn't exist, with no relevant documentation anywhere in the corpus.
2. The exact policy sentence needed is sitting in the top-retrieved chunk, and the model's answer still contradicts it.
3. The bot answers confidently, but cites a chunk about a *different*, similarly-named product.

---

## Part C — Build and Run a Dataset (15 min)

Using the schema from Day 1, build a `rows` list with **4 cases**:

1. A normal policy-QA case that should pass all 4 metrics
2. A hard negative for `faithfulness` (corrupt one fact in the response)
3. A case where `retrieved_contexts` is **empty** — predict what happens to `faithfulness` and `answer_relevancy` before running it
4. A `context_precision` hard negative: 3 retrieved chunks, only 1 relevant to the question

Annotate every row with `category`, `failure_mode`, and `is_hard_negative`. Run `evaluate()` and compare actual scores to your predictions.

---

## Part D — Map Back to Module 3/4 (10 min)

For each of the 4 RAGAS metrics, write one sentence naming the Module 3 failure mode or Module 4 DeepEval metric it's most analogous to, and one sentence on what's genuinely *new* about it in the RAG context.

---

## Self-Check

- [ ] You can explain, in your own words, why RAG needs 4 metrics instead of the 1-2 you used in Module 4
- [ ] Your dataset has at least 1 hard negative, and it actually scored low when you ran it
- [ ] You can say which RAGAS metric would have caught the Cursor incident from Day 1, and why
- [ ] You used the same `category`/`failure_mode`/`is_hard_negative` annotation habit from Module 4 Day 4 without being told to redo it from scratch
