# AI-Testing-APR

Notes, class planning, and hands-on projects from the **AI Testing, LLM Validation & Agent Evaluation** live training (40+ hours, April cohort).

This repo is my working notebook for the course — lecture notes, code samples, assignments, and project scaffolding live here, organized by module.

## Focus Areas

- LLM Testing
- RAG & Agentic RAG
- AI Agents
- Voice Agents
- Red Teaming & Adversarial Testing *(Module 8 — Promptfoo)*
- CI/CD for AI Evaluation with GitHub Actions *(Modules 2, 4, 8)*

## Tools Covered

- **Python** — test scripting and automation
- **DeepEval** — LLM and agent evaluation
- **RAGAS** — RAG pipeline evaluation
- **Promptfoo** — prompt regression, multi-model comparison, `redteam`
- **LangSmith** — tracing and observability
- **GitHub Actions** — CI/CD for automated evals

## Repo Structure

```
.
├── intro-demo/                  # Demo / intro session (pre-module)
├── module-01-intro-to-ai-llms/
├── module-02-python-for-ai-testing/
├── module-03-ai-testing-fundamentals/
├── module-04-deepeval-llm-testing/
├── module-05-ragas-rag-testing/
├── module-06-agentic-rag-testing/
├── module-07-deepeval-agent-testing/
├── module-08-adversarial-red-teaming/
├── module-09-voice-agent-testing/
├── .github/
│   └── workflows/          # CI/CD pipelines for automated evals
└── README.md
```

Each module folder contains:
- `notes.md` — lecture notes and concepts
- `examples/` — code walkthroughs from class
- `exercises/` — assignments and practice
- `resources.md` — links, papers, references

## Curriculum

### Module 1 — Introduction to AI and Large Language Models (3h)
- What is Artificial Intelligence?
- AI vs ML vs Deep Learning vs Generative AI
- Introduction to NLP
- What are Large Language Models?
- How LLMs work (high level)
- Tokens, embeddings, context window
- Prompt → Model → Response flow
- Popular models overview: GPT, Claude, Llama, Gemini
- Real-world LLM applications
- Traditional software vs AI systems

### Module 2 — Python for AI Testing & Automation (7h)
- Python installation and setup
- Virtual environments
- Variables and data types
- Functions and modules
- Lists, dictionaries, JSON
- File handling
- Exception handling
- Logging and debugging
- API testing using Python
- `.env` and secrets handling
- Intro to `pytest`
- Writing reusable test utilities
- Test data preparation
- Automation framework structure
- Batch execution scripts
- Reporting basics
- **CI/CD foundations with GitHub Actions**
  - Workflows, jobs, steps, triggers
  - Managing API keys with GitHub Secrets
  - Running `pytest` on push/PR
  - Caching dependencies
  - Publishing reports as workflow artifacts

### Module 3 — Fundamentals of AI Testing (3h)
- Traditional testing vs AI testing
- Deterministic vs probabilistic outputs
- Unique testing challenges
- Hallucination
- Bias and fairness
- Toxicity testing
- Prompt sensitivity
- Regression risks
- Model drift
- Privacy and compliance basics
- **Intro to red teaming & adversarial testing**
  - What is LLM red teaming? Goals and scope
  - OWASP Top 10 for LLMs overview
  - Threat categories: prompt injection, jailbreaks, data leakage, PII, bias elicitation
  - Manual vs automated attacks — when to use each

### Module 4 — LLM Testing with DeepEval (8h)
- Introduction to DeepEval
- Test cases
- Evaluators
- LLM-as-a-judge
- Rule-based evaluation
- Golden datasets
- Automated validation workflows
- Metrics: relevancy, faithfulness, correctness, hallucination, toxicity, bias, latency
- **DeepEval in CI**
  - Running DeepEval in a GitHub Actions workflow (`llm-eval.yml`)
  - Gating merges on eval scores

### Module 5 — RAG Testing using RAGAS (5h)
- What is RAG?
- Retriever + generator flow
- Chunking validation
- Embedding quality
- Vector database validation
- Groundedness testing
- Retrieval correctness
- Metrics: faithfulness, context precision, context recall, answer relevancy

### Module 6 — Agentic RAG Testing (2h)
- Multi-step retrieval, planner + executor flows
- Tool and memory validation
- Multi-hop reasoning and failure-path testing

### Module 7 — AI Agents Testing with DeepEval (3h)
- Function/tool calling validation, multi-step agent workflows
- Memory, context, and tool-selection correctness
- Agent failure and fallback testing
- DeepEval metrics: task completion, tool correctness, argument correctness, turn relevancy, conversation completeness
- **Agent-specific red teaming**
  - Tool / function-call abuse, indirect prompt injection via tool outputs
  - System-prompt leakage and data exfiltration through agents

### Module 8 — Adversarial Testing & Red-Teaming with Promptfoo (2h)
- **Day 1** — what adversarial testing & red-teaming are; installing Promptfoo; a first eval comparing **two prompts across two local Ollama models** with assertions
- **Day 2** — extensive testing of the Module 7 **trip agent** via a custom Python provider: functional + adversarial evals (capable agent, **free local Ollama judge**), executing and **visualising in the web UI** (`promptfoo view`)
- Attacks map to OWASP LLM01 (prompt injection), LLM07 (system-prompt leakage); deterministic tripwires + `llm-rubric`; defense-in-depth (provider content filters)
- *Going further:* automated `promptfoo redteam` (plugins/strategies) and CI gating (`promptfoo/promptfoo-action`)

### Module 9 — Voice Agent Testing (2h)
- **Day 1** — build a local voice agent: **Sarvam** STT + **Groq** LLM (fast/streaming) + **Sarvam** TTS, file-in/file-out with per-stage latency; intro to voice-specific testing
- **Day 2** — implement the tests: STT accuracy (**WER** with `jiwer`), the **TTS→STT round-trip**, latency-budget assertions, and fallback hard negatives (silence / gibberish / out-of-scope)
- The brain is tested as before (reuse Promptfoo/DeepEval on the transcript); what's new is ears, mouth, and latency — all still the Module 4 Day 4 testing mindset, with audio as the input

## Getting Started

```bash
# Clone
git clone <repo-url>
cd AI-Testing-APR

# Set up a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install shared dependencies (per-module requirements live in each folder)
pip install -r requirements.txt
```

Secrets (API keys for OpenAI, Anthropic, etc.) go in a local `.env` file — never commit it.

## Progress

- [x] Module 1 — Introduction to AI and LLMs
- [x] Module 2 — Python for AI Testing *(+ CI/CD basics)*
- [x] Module 3 — Fundamentals of AI Testing *(+ red-teaming intro)*
- [x] Module 4 — DeepEval *(+ CI)*
- [x] Module 5 — RAGAS
- [x] Module 6 — Agentic RAG
- [ ] Module 7 — Agents with DeepEval 
- [ ] Module 8 — Promptfoo *(+ redteam, CI)*
- [ ] Module 9 — Voice Agents

---

**Total Duration:** 40+ Hours
