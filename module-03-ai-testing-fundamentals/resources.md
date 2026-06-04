# Module 3 — Resources

## Core reading — AI testing fundamentals

- OWASP Top 10 for LLM Applications (2025) — https://owasp.org/www-project-top-10-for-large-language-model-applications/
- NIST AI Risk Management Framework — https://www.nist.gov/system/files/documents/2023/01/26/AI RMF 1.0.pdf
- MLCommons AI Safety benchmark — https://mlcommons.org/working-groups/ai-safety/ai-safety/
- "Sparks of Artificial General Intelligence" (Microsoft Research, 2023) — good survey of emergent capability risks — https://arxiv.org/abs/2303.12528

## Hallucination

- "Survey of Hallucination in Natural Language Generation" (Ji et al., 2023) — https://arxiv.org/abs/2202.03629
- TruthfulQA benchmark — measuring whether language models generate truthful answers — https://github.com/sylinrl/TruthfulQA
- Carlini et al. "Extracting Training Data from Large Language Models" (memorization / PII leakage) — https://arxiv.org/abs/2012.07805
- DeepEval hallucination metric docs — https://docs.confident-ai.com/docs/metrics-hallucination

## Bias and fairness

- "On the Dangers of Stochastic Parrots" (Bender et al., 2021) — the foundational bias critique — https://dl.acm.org/doi/10.1145/3442188.3445922
- BBQ (Bias Benchmark for QA) — https://github.com/nyu-mll/BBQ
- Winogender schemas (gender bias in coreference) — https://github.com/rudinger/winogender-schemas
- WinoBias — https://github.com/uclanlp/corefBias

## Toxicity testing

- Perspective API (Google) — toxicity classifier you can call programmatically — https://perspectiveapi.com
- RealToxicityPrompts dataset — https://allenai.org/data/real-toxicity-prompts
- ToxiGen — https://github.com/microsoft/TOXIGEN
- DeepEval ToxicityMetric — https://docs.confident-ai.com/docs/metrics-toxicity

## Prompt sensitivity

- "Large Language Models Are Not Robust Multiple Choice Selectors" — sensitivity analysis — https://arxiv.org/abs/2309.03882
- "Calibrate Before Use: Improving Few-Shot Performance of Language Models" — https://arxiv.org/abs/2102.09690
- Promptfoo sensitivity testing — https://www.promptfoo.dev/docs/guides/llm-testing

## Red teaming

- Microsoft PyRIT (Python Risk Identification Toolkit for generative AI) — https://github.com/Azure/PyRIT
- Garak — LLM vulnerability scanner — https://github.com/leondz/garak
- Anthropic's responsible scaling policy and red teaming notes — https://www.anthropic.com/news/anthropics-responsible-scaling-policy
- "Red Teaming Language Models to Reduce Harms" (Ganguli et al., 2022, Anthropic) — https://arxiv.org/abs/2209.07858
- "Jailbroken: How Does LLM Safety Training Fail?" (Wei et al., 2023) — https://arxiv.org/abs/2307.02483

## Prompt injection

- "Prompt Injection Attacks and Defenses in LLM-Integrated Applications" — https://arxiv.org/abs/2310.12815
- Simon Willison on prompt injection — comprehensive blog series — https://simonwillison.net/2022/Sep/12/prompt-injection/
- Indirect prompt injection research (Greshake et al., 2023) — https://arxiv.org/abs/2302.12173

## Privacy and PII

- "Quantifying Privacy Risks of Masked Language Models Using Split Shadow Training" — https://arxiv.org/abs/2203.12570
- Presidio (Microsoft PII detection library) — https://github.com/microsoft/presidio
- `scrubadub` Python PII scrubber — https://github.com/LeapBeyond/scrubadub

## Evaluation frameworks (preview of Modules 4–8)

- DeepEval — LLM evaluation framework — https://github.com/confident-ai/deepeval
- RAGAS — RAG evaluation — https://github.com/explodinggradients/ragas
- Promptfoo — prompt testing and redteam — https://www.promptfoo.dev
- Evals (OpenAI) — https://github.com/openai/evals
- LangSmith — tracing and evaluation for LangChain — https://smith.langchain.com

## Standards and compliance

- EU AI Act summary — https://artificialintelligenceact.eu
- GDPR guidance on automated decision-making — https://gdpr-info.eu/art-22-gdpr/
- HIPAA and AI considerations — https://www.hhs.gov/hipaa/index.html

## Courses and talks

- Chip Huyen "Designing Machine Learning Systems" — Chapter 8 (Data Distribution Shifts) — https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/
- "Evaluating and Debugging Generative AI" (DeepLearning.AI) — https://www.deeplearning.ai/short-courses/evaluating-debugging-generative-ai/
- DEFCON AI Village talks archive — https://aivillage.org
