# Module 4 — Resources: LLM Testing with DeepEval

---

## Official Documentation

- [DeepEval Documentation](https://docs.confident-ai.com) — full API reference, metric guides, CI integration
- [DeepEval GitHub Repository](https://github.com/confident-ai/deepeval) — source, examples, changelog
- [Confident AI Platform](https://app.confident-ai.com) — hosted dashboard for DeepEval results
- [DeepEval Metrics Reference](https://docs.confident-ai.com/docs/metrics-introduction) — all built-in metrics listed

---

## Key Papers

- [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685) — foundational paper on using LLMs to evaluate other LLMs. Read Section 3 on position bias and verbosity bias.
- [RAGAS: Automated Evaluation of Retrieval Augmented Generation](https://arxiv.org/abs/2309.15217) — the paper behind Module 5; introduces faithfulness, context precision, answer relevancy metrics
- [G-EVAL: NLG Evaluation using GPT-4 with Better Human Alignment](https://arxiv.org/abs/2303.16634) — the research behind DeepEval's GEval metric
- [Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073) — Anthropic paper on using AI to evaluate and improve AI outputs
- [Can LLMs Grade Their Own Papers?](https://arxiv.org/abs/2310.17631) — survey of LLM self-evaluation limitations

---

## Metrics Deep Dive

- [DeepEval — Answer Relevancy](https://docs.confident-ai.com/docs/metrics-answer-relevancy)
- [DeepEval — Faithfulness](https://docs.confident-ai.com/docs/metrics-faithfulness)
- [DeepEval — Hallucination](https://docs.confident-ai.com/docs/metrics-hallucination)
- [DeepEval — GEval](https://docs.confident-ai.com/docs/metrics-llm-evals) — how to write good evaluation criteria
- [DeepEval — Custom Metrics](https://docs.confident-ai.com/docs/metrics-custom)

---

## LLM-as-a-Judge

- [OpenAI Evals Framework](https://github.com/openai/evals) — OpenAI's own evaluation framework; same LLM-judge concept
- [Prometheus: Inducing Fine-grained Evaluation Capability in Language Models](https://arxiv.org/abs/2310.08491) — specialized judge LLMs that are cheaper than GPT-4
- [FairEval: Evaluating Fairness in LLM-based Evaluators](https://arxiv.org/abs/2305.17926) — known biases in LLM judges (position bias, verbosity bias, self-enhancement bias)
- [Chatbot Arena Leaderboard](https://chat.lmsys.org) — human preference rankings; useful for choosing judge models

---

## Golden Datasets & Benchmarks

- [MMLU (Massive Multitask Language Understanding)](https://arxiv.org/abs/2009.03300) — 57-subject benchmark; useful for factual recall baselines
- [TruthfulQA](https://arxiv.org/abs/2109.07958) — benchmark specifically for hallucination; 817 questions where models tend to confabulate
- [HaluEval](https://arxiv.org/abs/2305.11747) — hallucination evaluation benchmark with 35,000 cases
- [HellaSwag](https://arxiv.org/abs/1905.07830) — commonsense reasoning benchmark
- [DeepEval Synthesizer Docs](https://docs.confident-ai.com/docs/synthesizer-introduction) — auto-generate test cases from your documents

---

## CI/CD for AI Evaluation

- [DeepEval CI/CD Integration Guide](https://docs.confident-ai.com/docs/integrations-github-actions)
- [GitHub Actions Documentation](https://docs.github.com/en/actions) — workflows, secrets, artifacts, branch protection
- [Testing Machine Learning Systems: Code, Data and Models](https://madewithml.com/courses/mlops/testing/) — Made With ML guide on ML testing in production
- [ML Test Score: A Rubric for ML Production Readiness](https://research.google/pubs/pub46555/) — Google paper on testing ML systems in production

---

## Toxicity & Safety Evaluation

- [Perspective API](https://perspectiveapi.com) — Google's toxicity scoring API; useful baseline for ToxicityMetric calibration
- [BOLD: Dataset and Metrics for Measuring Biases in Open-Ended Language Generation](https://arxiv.org/abs/2101.11718) — bias evaluation dataset
- [HarmBench](https://www.harmbench.org) — standardized benchmark for LLM safety evaluation
- [LMSYS Vicuna Eval](https://lmsys.org/blog/2023-03-30-vicuna/) — 80 diverse test questions covering different domains

---

## Tools in the Ecosystem

- [LangSmith](https://smith.langchain.com) — LangChain's tracing and evaluation platform; complements DeepEval
- [Weights & Biases Prompts](https://wandb.ai/site/solutions/llmops) — LLM observability and evaluation
- [Arize Phoenix](https://phoenix.arize.com) — open-source LLM observability with eval support
- [TruLens](https://www.trulens.org) — RAG evaluation framework (alternative to RAGAS + DeepEval)
- [Braintrust](https://www.braintrust.dev) — LLM eval platform with dataset management

---

## Model Drift & Monitoring

- [The Hidden Dangers of LLM Model Updates](https://www.anthropic.com/news/claude-model-updates) — why pinning model versions matters
- [OpenAI Model Deprecation Policy](https://platform.openai.com/docs/deprecations) — understand when models change under you
- [Evidently AI](https://www.evidentlyai.com) — data and ML monitoring; apply same concepts to LLM drift detection

---

## Practice Datasets for This Module

| Dataset | Use for | Location |
|---|---|---|
| `data/golden_eval.json` | Day 3 EvaluationDataset exercises | `module-04-deepeval-llm-testing/data/` |
| Module 3 probe prompts | Red team + safety evals | `module-03-ai-testing-fundamentals/examples/` |
| TruthfulQA (subset) | Hallucination metric calibration | [huggingface.co/datasets/truthful_qa](https://huggingface.co/datasets/truthful_qa) |
