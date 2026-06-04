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
├── day-00-demo/                 # Demo / intro session (pre-module)
├── module-01-intro-to-ai-llms/
├── module-02-python-for-ai-testing/
├── module-03-ai-testing-fundamentals/
├── module-04-deepeval-llm-testing/
├── module-05-ragas-rag-testing/
├── module-06-agentic-rag-testing/
├── module-07-deepeval-agents/
├── module-08-promptfoo/
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

### Module 4 — LLM Testing with DeepEval (5h)
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

### Module 6 — Agentic RAG Testing (5h)
- Multi-step retrieval
- Planner + executor flows
- Tool validation
- Memory testing
- Multi-hop reasoning validation
- Failure path testing

### Module 7 — AI Agents Testing with DeepEval (5h)
- Function/tool calling validation
- Multi-step agent workflows
- Memory and context validation
- Tool selection correctness
- Intermediate reasoning validation
- Response consistency checks
- Agent failure and fallback testing
- DeepEval metrics: task completion, tool correctness, argument correctness, turn relevancy, conversation completeness
- **Agent-specific red teaming**
  - Tool / function-call abuse
  - Indirect prompt injection via tool outputs
  - System-prompt leakage and data exfiltration through agents
  - Unsafe tool-use probes

### Module 8 — Promptfoo for Prompt & Regression Testing (3h)
- YAML-based assertions
- Output validation
- Multi-model comparison
- Regression testing
- Safety prompt checks
- **Promptfoo `redteam`**
  - Jailbreak, prompt injection, PII leakage attack packs
  - Custom red-team configs
- **Promptfoo in CI**
  - `promptfoo eval` with pass/fail thresholds (`promptfoo.yml`)
  - Matrix builds for multi-model comparison
  - Scheduled red-team runs (`redteam-nightly.yml` via `cron`)
  - Posting results back to PRs as comments

### Module 9 — Voice Agent Testing (4h)
- Speech-to-text testing
- LLM response validation
- Text-to-speech testing
- Intent accuracy
- Latency testing
- Interruption and fallback testing

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
- [ ] Module 2 — Python for AI Testing *(+ CI/CD basics)*
- [ ] Module 3 — Fundamentals of AI Testing *(+ red-teaming intro)*
- [ ] Module 4 — DeepEval *(+ CI)*
- [ ] Module 5 — RAGAS
- [ ] Module 6 — Agentic RAG
- [ ] Module 7 — Agents with DeepEval *(+ agent red-teaming)*
- [ ] Module 8 — Promptfoo *(+ redteam, CI)*
- [ ] Module 9 — Voice Agents

---

**Total Duration:** 40+ Hours
