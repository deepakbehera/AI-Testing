# Module 7 — Resources: AI Agents Testing with DeepEval

---

## Carrying Forward From Modules 4-6

- Module 4 `examples/04_testing_mindset.ipynb` — equivalence partitioning, boundary value analysis, the coverage matrix, hard negatives. This module's `tool_selection_partitions` and `argument_contamination` partitions are directly derived from Day 4's technique. The coverage matrix in Day 2 is a direct extension of the one started there.
- Module 5 `notes.md`, Day 3 — the `@traceable` LangSmith pattern. Every tool in `examples/agent_tools.py` is decorated with `@traceable`; each invocation appears as its own child span under the agent trace. Same setup, now tracing tool calls instead of retrieval steps.
- Module 6 `examples/agent.py` — the planner/executor loop, `judge_client`/`judge_model` exposure pattern, and `.env` loading convention. `agent_tools.py` follows all the same patterns.
- Module 6 `examples/golden_dataset.json` — the schema that `module-07-deepeval-agent-testing/examples/golden_dataset.json` extends. The `eval_type` field now maps to specific DeepEval metric names instead of hand-rolled verdict classes.
- Module 6 `notes.md`, Day 2 — the three hand-rolled verdict functions (`MemoryRetentionVerdict`, `ReasoningChainVerdict`, `GracefulFailureVerdict`) and their explicit mapping to Day 2's DeepEval replacements.

---

## Real-World Incident Referenced in This Module

- [Air Canada ordered to honour discount from its chatbot (CBC News, February 2024)](https://www.cbc.ca/news/canada/british-columbia/air-canada-chatbot-bereavement-travel-policy-1.7116416) — the Civil Resolution Tribunal ruling that found Air Canada liable for its chatbot's incorrect bereavement-fare guidance, anchoring Day 1's `ToolCorrectnessMetric` discussion
- [BC Civil Resolution Tribunal decision — Moffatt v Air Canada (2024 BCCRT 149)](https://decisions.civilresolutionbc.ca/crt/crtd/en/item/519964/index.do) — the actual tribunal decision; Section 36 onward discusses the chatbot's misleading statements and why the airline was not excused by a disclaimer link to the correct policy page

---

## DeepEval Agent Metrics

- [DeepEval Agentic Metrics Overview](https://deepeval.com/docs/metrics-introduction#agentic-metrics) — official documentation covering Task Completion, Tool Correctness, Argument Correctness, Step Efficiency, Plan Adherence, and Plan Quality
- [DeepEval `LLMTestCase` + `ToolCall` API reference](https://deepeval.com/docs/evaluation-test-cases#tool-call) — how to construct `ToolCall` objects and attach them to test cases
- [DeepEval `evaluate()` function](https://deepeval.com/docs/evaluation-introduction) — running multiple metrics over a dataset in one call

---

## OpenAI Function-Calling (Tool-Calling) API

- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling) — the `tools` parameter, `tool_choice="auto"`, and the message loop used in `agent_tools.py`
- [OpenAI Tools API Reference](https://platform.openai.com/docs/api-reference/chat/create#chat-create-tools) — the JSON schema format for tool definitions

---

## LangSmith Tracing (continuity from Modules 5-6)

- [LangSmith Observability Docs](https://docs.langchain.com/langsmith) — tracing setup
- [LangSmith `@traceable` decorator](https://docs.langchain.com/langsmith/observability-quickstart) — now tracing individual tool calls; each `@traceable` tool appears as a separate child span in LangSmith's trace tree, enabling per-call inspection of name, args, and output
- [LangSmith Trace Filtering](https://docs.langchain.com/langsmith/how-to-guides/monitoring/filter-traces-in-application) — filtering traces by run type; tool runs have `run_type="tool"`, useful for isolating agent tool-call traces in production

---

## Foundational Papers on Agentic Tool Use

- [Toolformer: Language Models Can Teach Themselves to Use Tools (Schick et al., 2023)](https://arxiv.org/abs/2302.04761) — foundational paper on LLMs learning to call APIs; the failure modes discussed (wrong tool, wrong arguments) are named and analyzed here
- [WebGPT: Browser-Assisted Question-Answering with Human Feedback (Nakano et al., 2022)](https://arxiv.org/abs/2112.09332) — early empirical study of tool-calling agents at scale; demonstrates that "which tool to call" and "what to pass" are separate error types that require separate evaluation
- [ToolBench: Facilitating Large Language Models to Master 16000+ Real-World APIs (Qin et al., 2023)](https://arxiv.org/abs/2307.16789) — benchmark for tool-use evaluation; covers ToolCorrectnessMetric-style evaluation methods

---

## Agent Evaluation Frameworks

- [AgentBench: Evaluating LLMs as Agents (Liu et al., 2023)](https://arxiv.org/abs/2308.03688) — multi-task benchmark specifically for tool-calling agents; the "task completion" axis maps directly to `TaskCompletionMetric`
- [τ-Bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains (Yao et al., 2024)](https://arxiv.org/abs/2406.12045) — benchmark grounding tool-agent evaluation in realistic customer-service domains (directly relevant to this module's WidgetPro/TurboMax scenario)

---

## Bridge to Module 8

- [DeepEval Red Teaming Metrics](https://deepeval.com/docs/red-teaming-introduction) — the adversarial evaluation framework that Module 8 uses; Module 7's `LLMTestCase` format is unchanged, but the `input` field now contains adversarial probes instead of realistic queries
- [OWASP LLM Top 10 — LLM01: Prompt Injection](https://owasp.org/www-project-top-10-for-large-language-model-applications/) — Module 3's failure-mode vocabulary, now testable via adversarial inputs; Module 8 runs these as formal test cases
