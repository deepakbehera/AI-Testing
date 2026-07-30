# Course Summary — AI Testing, LLM Validation & Agent Evaluation

A concept-by-concept summary of the whole course. **The one idea that connects everything:**
> Testing an AI system is the *same discipline* as testing any software — partition the input space, test the edges, keep cases that *should* fail, measure with the right metric, and never trust a single number — applied to systems that are **probabilistic** instead of rule-based. We carried that idea from classical ML → LLMs → RAG → agents → adversarial → voice.

---

## Foundations — the developer setup

- **VS Code** — the editor/IDE: running Jupyter notebooks, selecting the right **Python interpreter / virtual environment** per project, integrated terminal, Python & Jupyter extensions.
- **Virtual environments (`venv`)** — one isolated environment per project so dependencies don't collide. `requirements.txt` pins deps; `.env` holds secrets and is **never committed**.
- **Git & GitHub** — version control (commits, branches, pull requests), `.gitignore` (keep out `.venv/`, `.env`, large/binary artifacts).
- **`pytest`** — the test runner used throughout: test functions, fixtures, `assert`, parametrization.
- **CI/CD with GitHub Actions** — workflows → jobs → steps → triggers (push/PR/schedule); API keys as **GitHub Secrets**; run tests/evals automatically; cache dependencies; publish reports as artifacts; **gate merges** on results.

---

## Module 1 — Introduction to AI & LLMs

- **AI vs ML vs Deep Learning vs Generative AI** — nested: AI ⊃ ML ⊃ DL; GenAI is DL that *produces* content.
- **NLP** — teaching machines to work with human language.
- **LLMs** — large neural networks trained to predict the next **token**; behavior is encoded in billions of weights, not readable rules.
- **Tokens** — sub-word units; models read/write tokens, not characters. **Embeddings** — numeric vectors capturing meaning (similar meaning → nearby vectors). **Context window** — how much text the model can "see" at once.
- **Prompt → Model → Response** — the core interaction loop.
- **Model landscape** — GPT (OpenAI), Claude (Anthropic), Llama (Meta), Gemini (Google).
- **Traditional software vs AI systems** — explicit rules (deterministic) vs learned behavior (probabilistic). This is *why* AI needs a different testing approach.

---

## Module 2 — Python for AI Testing & CI/CD

- Python essentials for testing: data types, functions/modules, **lists/dicts/JSON**, file handling, exceptions, logging/debugging.
- **API testing** in Python; **`.env`/secrets** handling.
- **`pytest`**: writing tests, reusable utilities, test-data prep, automation-framework structure, batch execution, reporting.
- **CI/CD foundations with GitHub Actions** (see Foundations) — run `pytest` on push/PR, secrets, caching, artifacts.

---

## Module 3 — Fundamentals of AI Testing

- **Deterministic vs probabilistic** — same input → same output (traditional) vs a *distribution* of outputs (LLM). Exact-match assertions are wrong by design.
- **Testing strategies for AI** — semantic assertions, behavioral contracts, distribution testing (run N times, measure pass rate), consistency testing (paraphrases), regression testing.
- **The 7 failure modes:** hallucination, bias/fairness, toxicity, prompt sensitivity, regression risk, **model drift**, PII/privacy leakage. These are *architectural properties*, not bugs — you **measure and manage**, not "fix."
- **Red-teaming** — adversarial testing; play the attacker to find weaknesses first.
- **OWASP LLM Top 10** — the security checklist (LLM01 Prompt Injection, LLM02 Sensitive Info Disclosure, LLM06 Excessive Agency, LLM07 System-Prompt Leakage, etc.).
- **Threat categories** — prompt injection (direct/indirect), jailbreaks, data leakage, bias elicitation. **Manual vs automated** red-teaming (both needed).

---

## Module 4 — LLM Testing with DeepEval + the Testing Mindset

- **The gap DeepEval fills:** you can't `assert "not hallucinating"` with string matching — you need another model to judge. **LLM-as-a-judge**.
- **`LLMTestCase`** — `input`, `actual_output`, `expected_output`, `context`/`retrieval_context`.
- **Metrics** — `AnswerRelevancyMetric`, `FaithfulnessMetric`, `HallucinationMetric`, `ToxicityMetric`, `BiasMetric`, correctness via **`GEval`**, `LatencyMetric`. Each has a **threshold**; a **score** (0–1); a **reason** (the judge's explanation — your debugging lifeline).
- **`GEval`** — write the rubric in plain English; an LLM judge scores against it. The general-purpose LLM-judge metric.
- **Golden datasets / `EvaluationDataset`** — a fixed, reusable set of cases run before/after every change (regression testing).
- **DeepEval in CI** — gate merges on eval scores.
- **THE TESTING MINDSET (Day 4 — the spine of the course):**
  - **Equivalence partitioning** — group inputs into classes; test one representative per class.
  - **Boundary value analysis (BVA)** — bugs cluster at the edges; test just inside/at/outside each boundary.
  - **Coverage matrix** — capability × failure-mode grid; a `0` cell is a *named, visible* gap.
  - **Hard negatives** — cases deliberately built so the *correct* behavior is to fail/refuse; proves your metric can actually detect failure.
  - Anchoring incidents: **Air Canada** (chatbot invented a refund policy) and **DPD** (chatbot talked into insulting its own company).

---

## Module 5 — RAG Testing with RAGAS

- **RAG** = **Retriever** (finds relevant chunks) + **Generator** (writes the answer from them). Two failure surfaces instead of one.
- **RAGAS 4 core metrics:**
  - `faithfulness` — does the answer stick to retrieved context? (generator)
  - `answer_relevancy` — does it address the question? (generator)
  - `context_precision` — of retrieved chunks, how many were relevant? (retriever)
  - `context_recall` — of all relevant chunks, how many were retrieved? (retriever; needs a reference)
- **Chunking** — splitting docs; the **chunk-boundary bug** (a fact split across two chunks can't be retrieved reliably). Strategies: fixed-size, recursive, semantic; overlap reduces (not eliminates) splits.
- **Embeddings & vector DBs** — validate that similar text → nearby vectors; **precision@k / recall@k** for retrieval correctness.
- **Groundedness** — is a claim backed by the source? (= faithfulness applied to what was retrieved).
- **Adversarial retrieval — corpus poisoning** (OWASP LLM08): malicious instructions injected into the knowledge base; fix is **access control**, not just prompting.
- **LangSmith tracing** — `@traceable`; the score is the *alarm*, the trace shows *which stage* broke.
- **RAGAS vs DeepEval** — RAGAS for retrieval-specific metrics; DeepEval for custom rubrics/rule-based checks; often both.

---

## Module 6 — Agentic RAG Testing

- **Agentic RAG** — a **planner** decides whether to retrieve again (loop), so the system can retrieve *multiple times* before answering.
- **New failure modes (only exist with a loop):**
  - **Infinite retrieval loop** — never decides it has enough.
  - **Premature stop** — answers after too few hops.
  - **Query drift** — reformulated queries wander off-intent.
  - **Reasoning-chain break** — every fact retrieved correctly but **combined wrong** (invisible to per-fact faithfulness checks).
- **Memory / context validation** — does an early-hop fact survive to the final answer? (the chunk-boundary bug, relocated to conversation memory).
- **Graceful failure** — when a hop finds nothing, admit it vs. fabricate. **Hops-required** is a new equivalence-partition dimension.
- Anchor incident: **Klarna** rolled back its AI support — fine on simple queries, degraded on complex multi-step cases.

---

## Module 7 — AI Agents Testing with DeepEval

- **Tool-calling agents** — the LLM picks a **function by name** and supplies **arguments**; new failure surface beyond "what it said."
- **DeepEval agent metrics** — Task Completion, **Tool Correctness** (right tool?), **Argument Correctness** (right args?), Step Efficiency, turn relevancy, conversation completeness.
- **Agent-specific red-teaming** — tool/function-call abuse, indirect prompt injection via tool outputs, system-prompt leakage / data exfiltration through agents, excessive agency.

---

## Module 8 — Adversarial Testing & Red-Teaming with Promptfoo

- **Adversarial testing** — inputs chosen to *make the system fail* (attacks), not typical use. **Red-teaming** — doing it systematically across an attack taxonomy. Same Module 4 Day 4 mindset on the **attack surface**.
- **Promptfoo** — a CLI for LLM **evals** and **red-teaming**, with a web UI. Config = `prompts` × `providers` × `tests` (with **assertions**); runs the full matrix.
  - **Assertions:** `contains`/`icontains`, `icontains-any`, `not-contains` (tripwires), `latency`, `llm-rubric` (LLM-as-judge). Negate with `not-`.
  - **Providers:** native (`ollama:chat:...`), or a **custom Python provider** (`call_api`) to wrap your own agent.
  - **Run:** `promptfoo eval`; **visualize:** `promptfoo view` (browsable matrix, filter failures, share).
  - **Red-team:** `promptfoo redteam init/run/report`; **plugins** (`owasp:llm`, `pii:*`, `harmful:*`, `hijacking`, `indirect-prompt-injection`) + **strategies** (`jailbreak`, `crescendo`, …). (Generation needs a free account.)
  - **CI:** non-zero exit gates the build; `promptfoo/promptfoo-action`.
- **Attacks → OWASP:** direct injection (LLM01), topic hijack, system-prompt/tool extraction (LLM07), PII (LLM06), jailbreak/**crescendo** (multi-turn escalation).
- **Defense in depth** — an attack can be blocked *upstream* (e.g., the model provider's content filter) before your agent even runs. Read **which layer** stopped it.
- Anchor incident: **Chevrolet** dealership chatbot talked into "selling" a car for **$1** (direct prompt injection).

---

## Module 9 — Voice Agent Testing

- **Voice agent** = **STT** (speech→text, "ears") → **LLM** ("brain") → **TTS** (text→speech, "mouth"). Three failure surfaces, and **latency dominates** the experience (why the LLM must **stream**).
- **Stack:** **Sarvam** (STT `saarika` / TTS `bulbul`, strong on Indian languages/accents) + **Groq** (fast, streaming LLM).
- **The brain is tested as before** (DeepEval/Promptfoo on the transcript). What's **new**:
  - **STT accuracy** — **WER/CER**; or judge transcript fidelity vs a known reference.
  - **TTS intelligibility** — **TTS→STT round-trip**: speak it, transcribe it back, judge if meaning survived.
  - **End-to-end latency** — assert budgets on per-stage timings (time-to-first-token, total).
  - **Speakable replies** — short, no markdown/lists (a bulleted answer is correct text but a broken voice reply).
  - **Turn-taking / interruption / fallback** (silence, gibberish, out-of-scope).
- **Key insight — transcription is the bridge:** you can't assert on a waveform, so STT turns speech into text you can judge (and it's the *measuring instrument* for the TTS test).
- **LLM-as-judge on voice** — DeepEval **`GEval`** grading reply quality, STT fidelity, TTS intelligibility (judge can run on a local/Groq model via `LocalModel`; run `async_mode=False` to avoid notebook event-loop issues).

---

## Bonus — Testing beyond LLMs

### Classical ML model testing
- **ML** learns rules from examples → you must test on **unseen data** (held-out **test set**).
- **Types:** supervised / unsupervised / reinforcement. Supervised splits into **regression** (predict a number) and **classification** (predict a category).
- **Regression metrics:** **MAE** (avg miss), **MSE** (punishes big misses), **RMSE** (√MSE, in target units), **R²** (fraction of variance explained; 1=perfect, 0=mean-baseline).
- **Classification metrics:** **confusion matrix** (TP/FP/FN/TN), **accuracy**, **precision**, **recall**, **F1**. **Accuracy lies** on imbalanced data (a majority-class dummy scores high but has 0 recall on the rare class) — precision/recall matter more.
- **Testing discipline:** train/validation/test split, **overfitting** (train≫test gap) vs underfitting, **cross-validation** (is the score stable, not luck?), **baselines** (beat a dummy), **data leakage** & **distribution shift/drift**.
- These are the classical roots of every LLM idea (test set → golden dataset; metrics → GEval; overfitting → demo-only agents; drift → model drift).

### Browser / E2E testing with Playwright
- Drives a real browser (Chromium/Firefox/WebKit) to test what users see.
- **Why it's a testing tool:** **auto-waiting** (no `sleep()`; kills flakiness), **locators** (`get_by_role`/`get_by_text`/`get_by_test_id`, robust to layout change), **web-first assertions** (`expect(...).to_...` auto-retry).
- **`pytest-playwright`** gives a `page` fixture; run headless (CI) or `--headed --slowmo` (debug/watch).
- Gotcha lesson: `get_by_role("checkbox").first` grabbed a hidden "toggle-all" — **scope your locators**.

---

## Cross-cutting themes (the "so what")

1. **Probabilistic ≠ untestable** — you test the *distribution*/*meaning*, not one exact string.
2. **LLM-as-a-judge** — grade meaning with another model (GEval, RAGAS, `llm-rubric`); pick a strong, independent judge.
3. **Metrics are the assert; the reason/trace is the diagnosis.**
4. **Hard negatives + coverage matrix** — prove failures are *detectable* and gaps are *visible*.
5. **Latency is a first-class metric**, especially for agents/voice.
6. **Security is layered** (defense in depth); red-teaming is systematic, not a lucky poke.
7. **Continuous evaluation** — drift means testing is ongoing (CI + scheduled runs), not one-and-done.

## Tools at a glance
VS Code · Git/GitHub/Actions · pytest · **DeepEval** (`GEval`, agent metrics) · **RAGAS** · **Promptfoo** (evals + redteam + UI) · **LangSmith** (tracing) · **Ollama** (local models) · **Sarvam** (STT/TTS) + **Groq** (LLM) · scikit-learn · Playwright.

---

# Appendix — Quick-Reference

## A. Metrics cheat-sheet

**LLM / RAG (DeepEval & RAGAS)**
| Metric | Measures | Direction | Needs |
|---|---|---|---|
| Answer Relevancy | addresses the question? | higher | input, output |
| Faithfulness | claims supported by context? | higher | output, retrieval_context |
| Hallucination | claims invented? | **lower** | output, context |
| Toxicity | harmful content? | **lower** | output |
| Bias | unfair generalizations? | **lower** | output |
| Correctness (`GEval`) | matches expected meaning? | higher | output, expected_output |
| Latency | response time | **lower** | latency |
| context_precision | retrieved chunks that were relevant | higher | + reference |
| context_recall | relevant chunks that were retrieved | higher | + reference |
| Tool Correctness | right tool chosen? | higher | tool calls, expected tools |
| Argument Correctness | right args passed? | higher | tool calls |

**Regression (ML)** — MAE, MSE, RMSE (all lower better, in/near target units) · R² (higher, 1=perfect, 0=mean baseline).
**Classification (ML)** — accuracy, precision, recall, F1 (higher better) · confusion matrix (TP/FP/FN/TN). *Accuracy misleads on imbalance → use precision/recall.*
**Voice** — WER/CER (lower better) · TTS→STT round-trip fidelity · latency budget (per-stage + total).

## B. Which tool when
| Goal | Reach for |
|---|---|
| Semantic LLM metrics, custom rubric, CI in pytest | **DeepEval** (`GEval`, `BaseMetric`) |
| Retrieval quality with ground truth (precision/recall) | **RAGAS** |
| Compare prompts/models, red-team, visual matrix, YAML | **Promptfoo** |
| See which pipeline step broke | **LangSmith** tracing |
| Free/local model (agent or judge) | **Ollama** |
| Browser / E2E user flows | **Playwright** |
| Predict a number/category on tabular data | **scikit-learn** (regression/classification) |

## C. Failure mode → how to test it
| Failure | Test |
|---|---|
| Hallucination | fact-grounding vs truth; Faithfulness in RAG |
| Bias | counterfactual name/gender/demographic swaps |
| Toxicity | indirect/jailbreak probes + toxicity metric |
| Prompt sensitivity | paraphrase suite (all pass) |
| Regression | golden dataset before/after change |
| Model drift | scheduled runs + canary prompts |
| PII leakage | canary injection; prompt-extraction probes; PII detector |
| Prompt injection | direct/indirect injection cases; tripwire on compliance markers |
| Retrieval miss | chunk-boundary boundary test; precision/recall@k |
| Reasoning-chain break | combination-aware check (not per-fact faithfulness) |
| Un-speakable voice reply | rule: no markdown/lists, ≤ N sentences |
| Flaky UI | Playwright auto-wait + web-first assertions (no `sleep`) |

## D. The through-line, restated
Held-out data → golden dataset · metrics → LLM-judge scores · data slices → equivalence partitions · minority cases → hard negatives · overfitting → demo-only agents · cross-validation → repeated eval runs · drift → continuous evaluation. **Same discipline, one new surface at a time.**
