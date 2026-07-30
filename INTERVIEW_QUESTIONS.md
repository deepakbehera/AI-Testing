# Interview Questions — AI Testing, LLM Validation & Agent Evaluation

A comprehensive interview-prep bank covering the whole course (foundations → Module 9 + bonus),
each question with a concise model answer. Pair with the [Course Summary](COURSE_SUMMARY.md).

**Difficulty:** 🟢 foundational · 🟡 intermediate · 🔴 advanced/senior.

**Contents**
 1. Foundations, Python, Git, CI/CD 
 2. AI/LLM fundamentals 
 3. AI testing strategy 
 4. Failure modes 
 5. Security, OWASP & red-teaming 
 6. DeepEval & metrics 
 7. The testing mindset 
 8. RAG & RAGAS 
 9. Agentic RAG & agents 
 10. Promptfoo 
 11. Tracing & observability 
 12. Voice agents 
 13. Classical ML testing 
 14. Playwright / E2E 
 15. Compare & contrast 
 16. Code-reading 
 17. Scenario / system design 
 18. Rapid-fire definitions

---

## 1. Foundations, Python, Git, CI/CD

**🟢 Why a virtual environment per project?**
Isolation — projects need different, sometimes conflicting, dependency versions (the bonus ML and Playwright topics each got their own). Reproducible via `requirements.txt`, disposable, no global pollution.

**🟢 Where do secrets live?**
A git-ignored `.env` locally; **GitHub Secrets** for CI. Never hard-coded or committed.

**🟢 What goes in `.gitignore` for this kind of repo?**
`.venv/`, `.env`, `__pycache__/`, notebook checkpoints, and generated/binary artifacts (audio `.wav`, screenshots, `results.json`, model files).

**🟡 Explain a GitHub Actions workflow end-to-end.**
`on:` triggers (push/PR/`schedule` cron/`workflow_dispatch`) → `jobs` → `steps`: checkout, setup-python, cache deps, install, inject secrets as env, run tests/evals, upload artifacts. Non-zero exit fails the check.

**🟡 How do you gate merges on tests?**
Enable branch protection → "require status checks to pass." If the eval/pytest job exits non-zero, the PR can't merge.

**🟡 Why cache dependencies in CI, and how?**
Speed/cost. `actions/cache` keyed on a hash of `requirements.txt` restores `~/.cache/pip` between runs.

**🟡 `pytest`: fixtures, parametrize, markers?**
Fixtures = reusable setup/teardown (e.g., a `page` or client). `@pytest.mark.parametrize` runs one test over many inputs (one pass/fail each). Markers (`@pytest.mark.slow`) group/skip tests.

**🔴 Why run expensive eval suites on a schedule, not just per-PR?**
To catch **model drift** — provider-side changes degrade quality with no code change. Nightly/weekly runs compare scores over time; per-PR runs catch code/prompt regressions.

**🟡 What's a good CI split for LLM tests?**
Fast deterministic checks on every push/PR; expensive multi-metric/LLM-judge and red-team suites nightly (marked `@expensive` or a separate workflow).

---

## 2. AI/LLM Fundamentals

**🟢 AI vs ML vs Deep Learning vs Generative AI?**
Nested (AI ⊃ ML ⊃ DL); GenAI is DL that *produces* content. LLMs are generative DL for language.

**🟢 Tokens, embeddings, context window?**
Tokens = sub-word units the model reads/writes; embeddings = meaning-vectors (similar → nearby); context window = max tokens attended to at once.

**🟡 Why is an LLM non-deterministic even at temperature 0?**
Floating-point/GPU non-associativity and infra differences make outputs not perfectly reproducible; temp 0 reduces but doesn't eliminate variance. Any temp > 0 samples fresh from the token distribution.

**🟡 What does temperature control?**
Randomness of sampling — low = focused/repeatable, high = diverse/creative. For reproducible tests use temp 0.

**🟡 Why do LLMs hallucinate?**
They're next-token probability machines; where training data is sparse they emit a *plausible* continuation with no built-in fact-checker.

**🟡 Why does prompt phrasing change output so much (prompt sensitivity)?**
Different wording → different tokenization and different high-probability continuations; small edits can shift behavior a lot. Test with paraphrase suites.

**🔴 What is RLHF and why does it matter for testing?**
Reinforcement Learning from Human Feedback tunes models to human preferences — it shapes safety/refusals and can introduce annotator bias, and providers update it silently (a drift source).

**🟢 Prompt → Model → Response — where does "logic" live?**
In billions of weights, not readable code — which is why you must test behavior on examples, not audit rules.

---

## 3. AI Testing Strategy

**🟢 Why can't you use exact-match assertions on LLM output?**
Output is a distribution; `assert output == "Paris"` is flaky by design. Test **meaning** and **contracts** instead.

**🟡 Name the AI-specific testing strategies.**
Semantic assertions (does it *mean* the right thing), behavioral contracts (must-include/exclude, length, sentiment), distribution testing (run N times, expect a pass rate), consistency testing (paraphrases agree), regression testing (golden suite before/after).

**🟡 What's a behavioral contract?**
A set of constraints an output must satisfy regardless of exact wording (must mention X, must not reveal Y, ≤ N chars, sentiment ≥ threshold).

**🟡 What are the five unique challenges of AI testing?**
Non-determinism, no ground truth, infinite input space, emergent behavior, evaluation lag (judge is slow/expensive/biased).

**🔴 How do you decide "what correct means" before testing?**
Define acceptance criteria up front — the reference answer or rubric, the metrics, and thresholds — because "good" is often subjective; without it, tests are unfalsifiable.

---

## 4. Failure Modes (define + how to test each)

**🟢 List the seven.**
Hallucination, bias/fairness, toxicity, prompt sensitivity, regression, model drift, PII/privacy leakage.

**🟡 Why "failure modes," not "bugs"?**
Emergent properties of training, not spec deviations — you measure/manage (grounding, guardrails, monitoring), not patch them away.

**🟡 How do you test for hallucination?**
Fact-grounding probes vs known truth; citation-existence checks; in RAG, faithfulness (claims must be supported by retrieved context).

**🟡 How do you test for bias?**
Counterfactual audits — matched prompts differing only by a demographic attribute (name/gender/religion); measure output/sentiment/decision divergence.

**🟡 How do you test toxicity if direct requests get refused?**
Indirect/jailbreak framings ("write a story where a character explains…"), plus a toxicity classifier/metric with a threshold.

**🟡 How do you catch model drift?**
Scheduled golden-suite runs + canary prompts with stable expected outputs; alert on score deltas over time.

**🟡 How do you test PII leakage?**
Canary injection (put a fake secret in the system prompt, assert it never appears in outputs); prompt-extraction probes; PII detectors on outputs; RAG cross-session isolation tests.

---

## 5. Security, OWASP & Red-Teaming Concepts

**🟢 What is red-teaming?**
Adopting the attacker's perspective to systematically find vulnerabilities before real attackers do.

**🟡 Direct vs indirect prompt injection?**
Direct = malicious instruction in the user message. Indirect = hidden in data the model retrieves/processes (docs, tool outputs, pages) — harder because retrieved content is treated as trusted.

**🟡 Name several OWASP LLM Top 10 entries.**
LLM01 Prompt Injection, LLM02 Sensitive Info Disclosure, LLM05 Improper Output Handling, LLM06 Excessive Agency, LLM07 System-Prompt Leakage, LLM08 Vector/Embedding Weaknesses, LLM09 Misinformation, LLM10 Unbounded Consumption.

**🟡 What is a jailbreak? Name families.**
Techniques that bypass safety training: persona/DAN, fictional framing, multi-turn escalation (**crescendo**), token-splitting/leetspeak, encoding (Base64), language switching, adversarial suffixes.

**🟡 What's the crescendo attack?**
Multi-turn: start benign, escalate gradually, using each small compliance as leverage — harder to catch because no single turn looks adversarial.

**🔴 What is the defender's dilemma?**
Defender must block **all** attack classes; attacker needs **one**. So red-teaming must be systematic (coverage), and a single passing test proves little.

**🔴 What is defense in depth for LLM apps?**
Layered safety: provider content filter → system-prompt guardrails → output filtering/tripwires → human confirmation for destructive actions. When an attack is blocked, know *which layer* did it.

**🟡 What is corpus poisoning and the real fix?**
Injecting malicious instructions into a RAG knowledge base (LLM08). Real fix = **access control** on who can edit the corpus; a test case detects it fast.

**🟡 Manual vs automated red-teaming?**
Manual surfaces novel/creative attacks (pre-launch, agents); automated scales known attack families in CI. Use both — manual findings feed the automated library.

---

## 6. DeepEval & Metrics

**🟢 What problem does DeepEval solve?**
You can't `assert "not hallucinating"` by string match — it provides **LLM-as-a-judge** metrics that score outputs 0–1 against thresholds.

**🟢 `LLMTestCase` fields?**
`input`, `actual_output`, `expected_output`, `context`/`retrieval_context`.

**🟡 Which metrics are "lower is better"?**
Toxicity, Hallucination, Bias (lower = safer/cleaner). Faithfulness, Relevancy, Correctness are higher = better. Always check direction before setting thresholds.

**🟡 Faithfulness vs Hallucination metric?**
Faithfulness = fraction of claims **supported** by context (higher better); Hallucination = fraction **invented** (lower better). Note: Faithfulness uses `retrieval_context`, Hallucination uses `context` (common trip-up).

**🟡 What is `GEval` and what makes a good criterion?**
A metric where you write the rubric in plain English and an LLM judge scores it. Good criteria: single dimension, anchored ("high looks like… low looks like…"), reference the specific params, positive-phrased for weak judges.

**🟡 `assert_test()` vs `evaluate()`?**
`assert_test` raises on failure (for pytest); `evaluate`/`EvaluationDataset.evaluate` runs all cases and returns aggregate results (for reports).

**🟡 Why `include_reason=True`?**
The score is the alarm; the **reason** is the diagnosis — it tells you which claim was flagged and why, essential for debugging a 2am CI failure.

**🟡 How do you build a custom rule-based metric?**
Subclass `BaseMetric`, implement `measure`/`is_successful`/`a_measure` — for deterministic checks (keyword coverage, JSON format, length) that need no LLM.

**🔴 How do you choose the judge model?**
Prefer a **stronger, independent** model than the one under test (don't grade own homework); mind judge biases (position/verbosity/self-enhancement); back semantic judgments with deterministic tripwires. In the voice module we pointed DeepEval's judge at Groq via `LocalModel`.

**🔴 GEval failed in Jupyter with an asyncio error — what fixed it and why?**
Set `async_mode=False`. GEval's async path uses `nest_asyncio`+`asyncio.wait_for`, which breaks on some Python/Jupyter combos; the sync path avoids it.

---

## 7. The Testing Mindset (Module 4 Day 4)

**🟢 Equivalence partitioning for prompts?**
Group the infinite input space into classes expected to behave alike (length, language, question type, context availability), test one representative per class.

**🟡 Boundary value analysis — LLM examples?**
Empty prompt; prompt at the exact token limit; "just enough" vs "missing the one needed sentence" of context; a request right at the refusal line.

**🟡 What is a hard negative and why essential?**
A case built so the *correct* behavior is to fail/refuse. Without one you can't distinguish "model is great" from "metric can't detect failure"; it also locks a fix as a regression test.

**🟡 What does a coverage matrix give you?**
Capability × failure-mode grid; a `0` cell is a named, visible gap — turns "we probably tested that" into a number.

**🔴 How is a hard negative like mutation testing?**
Both intentionally introduce a defect to confirm the tests *notice* — if a hard negative passes, your metric/threshold isn't sensitive enough.

**🟡 How do you turn one seed test case into a coverage cluster?**
Systematic mutations: paraphrase, negation, distractor context, missing context, contradictory context, adversarial framing, format stress, out-of-scope.

---

## 8. RAG & RAGAS

**🟢 What is RAG and its two stages?**
Retrieval-Augmented Generation: a **retriever** finds relevant chunks, a **generator** answers from them. Two failure surfaces.

**🟡 The four RAGAS metrics and which stage each tests?**
`faithfulness` + `answer_relevancy` → generator; `context_precision` (retrieved-that-were-relevant) + `context_recall` (relevant-that-were-retrieved) → retriever.

**🟡 context_precision vs context_recall?**
Precision = of what you retrieved, how much was relevant (noise control). Recall = of all relevant docs, how many you found (completeness). Independent.

**🟡 precision@k vs recall@k?**
precision@k = relevant among top-k; recall@k = fraction of all relevant found in top-k.

**🟡 What is the chunk-boundary bug and how do you catch/mitigate it?**
A fact split across two chunks so neither contains it whole → retrieval misses it. Catch with a boundary test placing a fact at a chunk edge; mitigate with overlap or semantic chunking (reduces, not eliminates).

**🟡 Chunking strategies?**
Fixed-size (simple, blind to structure), recursive (respects paragraphs/sentences), semantic (splits where embedding similarity drops — best, costlier).

**🟡 How do you validate an embedding model?**
Sanity-check that semantically similar text scores high similarity and dissimilar text scores low; watch for lexical-overlap false positives/negatives (TF-IDF fails true paraphrases).

**🟡 What is groundedness?**
Whether a claim is backed by source material — faithfulness applied to what was actually retrieved.

**🟡 RAGAS vs DeepEval — when each?**
RAGAS for retrieval-specific ground-truth metrics; DeepEval for custom rubrics/rule-based/non-RAG. Often both, sharing one dataset schema.

**🔴 A RAG answer is wrong — how do you localize retriever vs generator?**
Check context precision/recall and the trace: right chunk retrieved but ignored → generator; wrong/missing chunk → retriever. Determines whether you fix chunking/retrieval or the prompt.

---

## 9. Agentic RAG & Tool-Calling Agents

**🟢 Agentic RAG vs plain RAG?**
A **planner** can loop — retrieve again, reformulate — before answering, enabling multi-hop questions.

**🟡 Failure modes unique to the loop?**
Infinite loop, premature stop, query drift, reasoning-chain break.

**🟡 Why can't faithfulness catch a reasoning-chain break?**
Each fact is individually grounded; the error is the **combination**. Needs a combination-aware/reasoning-level check.

**🟡 What's new to test in a tool-calling agent?**
Tool correctness (right tool), argument correctness (right args), step efficiency, task completion — not just the final text.

**🟡 How do you test agent memory across turns?**
A follow-up that only resolves with context ("…is it cold *there* at night?"); assert on-topic; check an early-hop fact survives to the final answer.

**🟡 What is graceful failure and how do you test it?**
When a hop finds nothing, the agent should admit it, not fabricate. Feed empty/no-answer inputs and assert a hedged/deflecting response (hard negative).

**🔴 What is the ReAct pattern?**
Reason → Act (call a tool) → Observe → repeat — the loop most agentic systems use; each step is traceable and testable.

---

## 10. Promptfoo

**🟢 What is Promptfoo and its two modes?**
An open-source CLI for LLM **evals** (compare prompts/models with assertions) and **red-teaming** (auto-generate attacks), with a web UI.

**🟡 Structure of a `promptfooconfig.yaml`?**
`prompts` × `providers` × `tests` (each with `assert`); runs the full matrix. `defaultTest` applies shared asserts/options.

**🟡 Key assertion types?**
`contains`/`icontains`, `icontains-any`, `not-contains`/`not-icontains` (tripwires), `equals`, `is-json`, `latency`, `javascript`/`python`, `similar`, `llm-rubric`. Prefix `not-` to negate.

**🟡 Deterministic assertion vs `llm-rubric`?**
Deterministic = cheap/exact/no model (leak markers, formats, timing); `llm-rubric` = semantic quality via a judge. Adversarial rows rely on tripwires because small judges misgrade.

**🟡 How do you test your own agent with Promptfoo?**
A **custom Python provider**: a file with `call_api(prompt, options, context) -> {"output": ...}` referenced as `file://provider.py`; set `PROMPTFOO_PYTHON` to the right venv.

**🟡 How do you use a free local judge?**
Set `defaultTest.options.provider` to `ollama:chat:<model>` — the agent under test keeps its own model; only grading is local/free.

**🟡 Red-team plugins vs strategies?**
Plugins = vulnerability generators (`owasp:llm`, `pii:*`, `harmful:*`, `hijacking`, `indirect-prompt-injection`); strategies = how attacks are wrapped/escalated (`jailbreak`, `jailbreak:composite`, `crescendo`, `basic`).

**🟡 How does Promptfoo fit CI?**
`promptfoo eval` exits non-zero on failing assertions (gates the build); official `promptfoo/promptfoo-action`; schedule red-team nightly via cron.

**🔴 You attacked an agent on Azure and a jailbreak row "errored." What happened?**
The **provider's content filter** blocked the prompt (`finish_reason: content_filter`) before the agent ran — defense in depth. Handle it as a resisted attack, not a test bug.

---

## 11. Tracing & Observability

**🟢 Why trace an LLM pipeline?**
The metric is the alarm; the trace shows *which step* broke — essential once there are multiple stages (retrieve → generate, or multi-hop).

**🟡 What does LangSmith `@traceable` do?**
Wraps a function as a trace **span** (with `run_type` like `retriever`/`llm`/`chain`/`tool`); nested calls become child spans visible in the UI. It's a no-op without a key, so code runs the same.

**🟡 Which env vars enable it?**
`LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY`, optional `LANGSMITH_PROJECT`.

**🔴 When is tracing more valuable than the metric's `reason`?**
Multi-step systems (agentic RAG, voice) — you need to see *which chunks were retrieved* or *which tool was called* to attribute a failure to retrieval vs generation vs tool use.

---

## 12. Voice Agents

**🟢 Describe the pipeline and failure surfaces.**
STT (ears) → LLM (brain) → TTS (mouth); three failure points, and latency dominates UX.

**🟢 Why must the LLM stream for voice?**
So speech can start before the model finishes thinking — a multi-second silent pause feels broken.

**🟡 What's the same vs new vs text testing?**
Brain = same (DeepEval/Promptfoo on transcript). New = STT accuracy, TTS intelligibility, end-to-end latency, turn-taking/interruption, fallback.

**🟡 Why is "transcription the bridge"?**
You can't assert on a waveform; STT turns speech into text you can judge — and it's the measuring instrument for the TTS round-trip.

**🟡 How do you test STT accuracy?**
Reference audio + known transcript → **WER/CER**; or an LLM fidelity judge comparing transcript vs reference (a changed place/number = fail).

**🟡 How do you test TTS intelligibility without a human?**
**TTS→STT round-trip**: synthesize a line, transcribe it back, judge if the meaning (names/numbers) survived.

**🟡 What's a "speakable reply" and why test it?**
Short, conversational, no markdown/lists/symbols — a bulleted answer is correct text but a broken voice reply.

**🟡 Which latency signals matter?**
Time-to-first-token/first-audio and total turn; break down per stage (STT/LLM/TTS) to find the bottleneck; target sub-~2s.

**🟡 What are endpointing, barge-in, and code-switching?**
Endpointing = detecting when the user stopped speaking; barge-in = user talking over the agent (it should stop and listen); code-switching = mixing languages in one utterance (a hard STT case).

**🔴 Caveat of the TTS→STT round-trip?**
It uses the ears (STT) to judge the mouth (TTS) — a failure could be either. That's why STT is tested separately; when a round-trip fails, listen to the clip.

---

## 13. Classical ML Testing (Bonus)

**🟢 Why test ML on unseen data?**
It learns from examples; scoring on training data measures memorization. Held-out test set estimates real performance.

**🟢 Types of ML and where regression/classification fit?**
Supervised / unsupervised / reinforcement. Supervised → regression (number) or classification (category).

**🟡 Regression metrics?**
MAE (avg abs miss), MSE (squared, punishes big misses), RMSE (√MSE, target units), R² (variance explained; 1 perfect, 0 = mean baseline, <0 worse than mean).

**🟡 Classification metrics + the confusion matrix?**
TP/FP/FN/TN → accuracy, precision (of predicted-positive, how many right), recall (of real positives, how many caught), F1 (harmonic mean).

**🟡 Why does accuracy lie, and the fix?**
On imbalance, always-predict-majority scores high accuracy but 0 recall on the rare class. Use precision/recall (and choose which matters — recall for cancer/fraud).

**🟡 Overfitting vs underfitting — detect how?**
Overfitting = memorized (train ≫ test); underfitting = too simple (poor on both). The **train-minus-test gap** is the alarm.

**🟡 Why cross-validation and baselines?**
CV checks the score is stable across folds (not one lucky split); a dummy baseline proves the model adds value.

**🟡 What is data leakage?**
Test/future info sneaking into training (e.g., scaling on the full dataset before splitting) — inflated scores that collapse in prod. Split first, fit preprocessing on train only.

**🔴 Map classical ML testing to LLM testing.**
Test set → golden dataset; metrics → GEval/RAGAS; overfitting → demo-only agents; cross-val → repeated eval runs; leakage → test-set contamination; drift → model drift.

---

## 14. Playwright / E2E (Bonus)

**🟢 Why is Playwright a *testing* tool, not just a scraper?**
Auto-waiting (waits for actionable elements — kills `sleep()` flakiness), locators (by role/text/test-id, robust to layout), web-first assertions (`expect(...)` auto-retries).

**🟡 What are locators and which do you prefer?**
Durable, meaning-based element handles: `get_by_role`, `get_by_text`, `get_by_label`, `get_by_test_id` — preferred over brittle CSS/XPath.

**🟡 What is a web-first assertion?**
`expect(locator).to_have_text(...)` retries until it passes or times out — no manual waits, no racing the page.

**🟡 Sync vs async API — when each?**
Sync for scripts/pytest (the norm). Async (`async_playwright`) in environments with a running event loop (e.g., Jupyter notebooks).

**🟡 Headless vs headed?**
Headless = no window (CI, fast). `--headed --slowmo` = visible/slowed for debugging or demos.

**🟡 What does `pytest-playwright` provide?**
A `page` fixture (fresh page per test) + CLI flags (`--headed`, `--slowmo`, `--browser`), keeping E2E tests short.

**🔴 A real locator gotcha?**
`get_by_role("checkbox").first` grabbed TodoMVC's hidden "toggle-all" and completed everything → scope locators (to the first list item) and know the DOM.

---

## 15. Compare & Contrast

- **Functional vs adversarial testing** — cooperative input, is the answer good? vs hostile input, does it stay safe/on-task?
- **DeepEval vs RAGAS** — general LLM/agent metrics + custom rubrics vs retrieval-specific ground-truth metrics.
- **DeepEval vs Promptfoo** — Python metrics/CI-in-pytest vs YAML matrix + web UI + built-in red-team.
- **Faithfulness vs answer relevancy** — grounded in context? vs addresses the question?
- **Context precision vs recall** — retrieved-relevant vs relevant-retrieved.
- **Precision vs recall (classification)** — of predicted-positive right? vs of real positives caught?
- **Overfitting vs drift** — memorized training data (your fault) vs provider changed under you.
- **Direct vs indirect injection** — user message vs retrieved data.
- **Jailbreak vs prompt injection** — erode safety refusals vs override system instructions.
- **Headless vs headed (Playwright)** — CI speed vs visible debugging.
- **Sync vs async Playwright** — scripts/pytest vs notebooks/event loops.

---

## 16. Code-reading / "what's wrong / what does this do"

**🟡 `assert response == "Paris"` for an LLM answer — what's wrong?**
Exact match on probabilistic output — flaky; "Paris, France" or "The capital is Paris" fail. Use semantic/GEval correctness.

**🟡 `expect(page.get_by_role("checkbox").first).to_be_checked()` on TodoMVC — risk?**
`.first` may be the toggle-all checkbox, not a todo's — scope the locator.

**🟡 In RAG tests, you compute scaling stats on the whole corpus then split — problem?**
Data leakage — test info influenced training. Split first, fit on train only.

**🟡 A GEval criterion says "the response should be good." Improve it.**
Too vague/multi-dimensional. Make it single-dimension and anchored: "The response answers the question directly, with no unrelated topics; high = concise+on-topic, low = rambling/off-topic."

**🟡 `time.sleep(2)` before checking an element in a UI test — what to use instead?**
Nothing — Playwright auto-waits; use a web-first `expect(...)` assertion that retries.

**🟡 A jailbreak test passes (agent refused) but the small Ollama judge marked it FAIL — why, and mitigation?**
Weak judge misgraded (especially negated rubrics). Positive-phrase the rubric and add a deterministic `not-contains` tripwire as the reliable gate.

---

## 17. Scenario / System Design

**🔴 Design an evaluation pipeline for a customer-support RAG bot going to production.**
Golden dataset annotated by capability × failure mode; RAGAS (retriever) + DeepEval (faithfulness/relevancy/safety) in CI gating PRs; hard negatives for injection/PII as regression tests; tracing for observability; scheduled drift runs + canary prompts; dashboards on score trends; human review of low-confidence/flagged cases.

**🔴 A stakeholder says "it passed all tests, ship it."**
Ask: happy-path only? Where are hard negatives/adversarial cases? What's the coverage matrix (which cells are 0)? What's the pass *rate* over repeated runs? Is there a drift schedule and a red-team suite?

**🔴 Users report the bot occasionally leaks another customer's data. How do you reproduce and prevent regression?**
Reproduce with a cross-session/RAG-isolation probe and canary injection; confirm the leak; record it as a hard negative with a `not-contains` tripwire; add access-control/output-filter fix; gate CI so the case must pass forever.

**🔴 You upgraded the underlying model and quality "feels off." How do you tell?**
Differential testing — run the same golden dataset against v1 and v2, diff per-case scores; inspect regressions (e.g., format/citation changes); decide with data, not vibes.

**🔴 Your voice agent feels laggy. How do you diagnose and fix?**
Measure per-stage `timings_ms` (STT/LLM/TTS + time-to-first-token); find the slowest stage; enable streaming, pick a faster model/provider, or a streaming STT/TTS; assert a latency budget in CI so it can't regress.

**🔴 How would you red-team an agent with tool access?**
Systematic taxonomy: direct/indirect injection, tool/function-call abuse, argument tampering, system-prompt/tool-name extraction, excessive agency (destructive actions), PII exfiltration via tool outputs; automate with Promptfoo redteam; record findings as hard negatives; add least-privilege + human confirmation.

**🔴 Choose metrics for a medical-triage classifier and justify.**
Prioritize **recall** on the dangerous class (a miss is catastrophic), watch precision to limit false alarms, report the confusion matrix, and beat a strong baseline; accuracy alone is misleading on imbalance.

---

## 18. Rapid-fire definitions

Hallucination · Faithfulness · Groundedness · Golden dataset · Hard negative · Coverage matrix · Equivalence partitioning · Boundary value analysis · LLM-as-a-judge · GEval · Threshold · Tripwire · Prompt injection (direct/indirect) · Jailbreak · Crescendo · System-prompt leakage · Corpus poisoning · Defense in depth · Model drift · Context window · Token · Embedding · Chunking · precision@k / recall@k · context precision / recall · Tool correctness · Argument correctness · Reasoning-chain break · Query drift · Premature stop · WER/CER · TTS→STT round-trip · Endpointing · Barge-in · Speakable reply · Auto-waiting · Web-first assertion · Locator · Overfitting · Cross-validation · Data leakage · Confusion matrix · Precision/Recall/F1 · MAE/RMSE/R².

> Be able to define each in one sentence *and* say how you'd test for it — that pairing is what interviewers probe for.
