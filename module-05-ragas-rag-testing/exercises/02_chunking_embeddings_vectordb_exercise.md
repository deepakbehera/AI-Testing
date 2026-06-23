# Exercise: Chunking, Embeddings & Vector DB Validation

**Estimated time:** 40–50 minutes

---

## Part A — Find the Boundary (15 min)

Using `fixed_size_chunk()` from the Day 2 notebook and the same `document`/`fact` from the example:

1. Binary-search the `chunk_size` parameter (keeping `overlap=0`) to find the **exact** range of `chunk_size` values where the fact gets split across two chunks. Report the range.
2. Outside that range — both smaller and larger `chunk_size` — confirm the fact lands fully inside one chunk. Explain in one sentence why *both* directions can fix it, and why a real document (with facts at unpredictable positions) can't rely on guessing the right chunk size.
3. Fix it instead with overlap: find the **minimum** `overlap` value (keeping the original boundary-triggering `chunk_size`) that gets the fact fully into at least one chunk.

---

## Part B — Precision/Recall Trade-offs (10 min)

Using `precision_at_k()` / `recall_at_k()`, construct three retrieval scenarios by hand (pick your own `retrieved` lists and `relevant` sets):

1. A retriever with **perfect precision, weak recall** (everything retrieved is relevant, but most relevant chunks are missed)
2. A retriever with **perfect recall, weak precision** (every relevant chunk is retrieved, buried among many irrelevant ones)
3. A retriever that's mediocre at both

For each, write one sentence on what a *user* would actually experience as a result (not just the numbers).

---

## Part C — Embedding Sanity Check, Adversarially (15 min)

Extend the Day 2 embedding sanity-check cell with your own sentences:

1. Add a pair of sentences that are **true paraphrases with zero shared vocabulary** (like the Day 2 example) from a domain of your choosing (not refunds).
2. Add a pair that are **lexically similar but semantically different** — e.g. "The conference starts at 9 AM" vs. "The conference *doesn't* start at 9 AM."
3. Run TF-IDF similarity on both pairs. Does TF-IDF correctly distinguish case 2's negation, or does it score them as similar because of shared words? What does that tell you about testing an embedding model specifically for negation handling?

---

## Part D — Extend the Coverage Matrix (10 min)

Add at least 4 new rows to `annotated_cases` covering a domain of your choice (not refunds/policy). Make sure:
- At least 2 different `category` values
- All 4 failure modes (`hallucination`, `chunk_boundary_split`, `low_precision`, `low_recall`) appear at least once
- At least one cell in the resulting matrix is deliberately left at `0` — and you can name, in one sentence, whether that's an acceptable gap or a real one

---

## Self-Check

- [ ] You found the exact `chunk_size` range that triggers the boundary bug, not just one example of it
- [ ] You can explain why precision and recall are independent, using your own retrieval scenario, not the notebook's
- [ ] You found at least one case where TF-IDF's lexical-only matching gives a misleading similarity score
- [ ] Your extended coverage matrix has a `0` cell you can justify, the same way Module 4 Day 4 asked you to justify gaps
