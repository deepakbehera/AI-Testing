# Day 0 — Demo Class Notes

Welcome. This is your takeaway from the Day 0 demo session. Use it as a quick reference, a study aid, and a starting point for the 40+ hour course that follows.

---

## What this session was about

AI systems — especially Large Language Models (LLMs) — don't behave like traditional software. The same input can produce different outputs, the system rarely crashes when it's wrong, and users tend to trust confident-sounding answers. That makes **testing AI a different discipline** from the software testing you may already know.

Today's goal was to give you the mental model, not the tools. The tools come next.

---

## 5 things to remember

1. **AI doesn't crash — it confidently gives wrong answers.** Silent failure is the default failure mode.
2. **Same prompt ≠ same answer.** LLMs are probabilistic. Your tests have to account for that.
3. **Assertions become heuristics.** Instead of `assertEquals`, you check for *behaviour*: keywords, tone, safety, factuality.
4. **60% of AI testing you already know.** Test case → prompt. Scenario → variation. Regression → prompt or model change. The mindset transfers.
5. **You don't need an ML background.** You need a tester's mindset — structured thinking, curiosity about failure modes, and comfort with ambiguity.

---

## Key terms from today

| Term | What it means |
|---|---|
| **LLM** | Large Language Model (e.g. GPT, Claude, Llama). Generates text token-by-token based on probability. |
| **Prompt** | The input you send to an LLM. The "test input" in AI testing. |
| **Non-determinism** | Same prompt, different outputs. Caused by sampling + temperature. |
| **Temperature** | A knob (0–1+) that controls how random the output is. 0 = most deterministic, 1+ = more creative. |
| **Hallucination** | When the model generates plausible-sounding but false information. |
| **Bias** | Systematic unfairness in outputs (gender, race, culture, politics, etc.). |
| **Toxicity** | Harmful, offensive, or unsafe content in outputs. |
| **Safety refusal** | When the model declines to answer a harmful request. |
| **Red teaming** | Deliberately trying to break an AI system — prompt injection, jailbreaks, bias probes. |
| **Soft assertion** | A check for a *property* of the response (e.g. contains key terms) rather than an exact-string match. |
| **LLM-as-a-judge** | Using one LLM to evaluate another LLM's output. Useful but needs verification. |
| **RAG** | Retrieval-Augmented Generation — an LLM that pulls in external documents before answering. |
| **Agent** | An LLM that can call tools / APIs and take multi-step actions. |

---

## What we demoed

### Demo 1 — Non-determinism
We sent the same prompt (*"Explain blockchain in simple terms"*) to the same local LLM **five times** and streamed each response. You saw:
- Different wording each run
- Different levels of depth
- **Same tone of confidence** — the model sounded equally sure in every version

**Lesson:** A string-match test would fail on 4 of 5 runs — but all 5 may be *correct* answers. AI testing has to measure behaviour, not exact strings.

### Demo 2 — Simple automation
We ran four test cases through the LLM in a loop with soft assertions:

| Test case | What we checked | Why it matters |
|---|---|---|
| `blockchain-basic` | Response contains "block", "chain", "ledger", or "distributed" | Keyword-based correctness |
| `math-simple` | Response contains "4" | Basic factual check |
| `hallucination-probe` | Asks *"Who is the current president of Mars?"* — expects the model to say no such thing | Catches hallucinations |
| `safety-refusal` | Asks for harmful instructions — expects a refusal | Catches unsafe compliance |

**Lesson:** An AI test suite is just **loop + LLM call + soft assertions + report**. That's it. Frameworks like DeepEval, RAGAS, and Promptfoo are sophisticated versions of exactly this pattern.

---

## Traditional testing vs AI testing — side by side

| | Traditional | AI |
|---|---|---|
| Output | Deterministic (same input → same output) | Probabilistic (same input → varied output) |
| Assertion | Exact match | Acceptable range, soft assertion |
| Result | Binary pass/fail | Degrees of quality & safety |
| Failure mode | Loud (crashes, error codes) | Silent (confident wrong answers) |
| Bug reproduction | Usually easy | Often hard — may only happen some of the time |

---

## Try the demos yourself

You'll need:
- Python 3.10+
- [Ollama](https://ollama.com) (runs LLMs locally — no API key, no cost)

```bash
# 1. Install Ollama from https://ollama.com, then:
ollama pull llama3.2:3b
ollama serve                       # keep this running in a separate terminal

# 2. Clone this repo and set up the Python env
cd day-00-demo
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # defaults to Ollama — no edits needed

# 3. Run the demos
python examples/live_demo_same_prompt.py
python examples/simple_automation.py
```

See [resources.md](resources.md) for the full setup cheatsheet and how to switch to OpenAI or Anthropic later.

### Exercises to try on your own
- Change `PROMPT` in [live_demo_same_prompt.py](examples/live_demo_same_prompt.py) and watch how different kinds of questions produce different kinds of variation.
- Add a new test case to [simple_automation.py](examples/simple_automation.py) — for example, *"Translate 'Hello' to French"* with `must_include=["bonjour"]`.
- Lower `temperature` to `0` and see how much (or how little) the variation shrinks.
- Swap `DEMO_MODEL` to `qwen2.5-coder:3b` and compare.

---

## What comes next in the course

This demo was a preview. Over the next 40+ hours you'll move from "seeing the problem" to "owning the solution":

- **Module 1** — Foundations of AI, LLMs, and how they actually work
- **Module 2** — Python + pytest for AI test automation, plus GitHub Actions CI
- **Module 3** — AI testing fundamentals, including an intro to red teaming
- **Module 4** — DeepEval (LLM-as-a-judge, golden datasets, metrics)
- **Module 5** — RAGAS for RAG pipeline testing
- **Module 6** — Agentic RAG testing
- **Module 7** — Agent testing (tool calls, memory, agent-specific red teaming)
- **Module 8** — Promptfoo for prompt regression + automated red teaming
- **Module 9** — Voice agent testing

By the end you'll have built a real, end-to-end AI test suite — LLM + RAG + agents + voice — wired into CI.

---

## Further reading

- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) — the canonical list of LLM security risks
- [Ollama](https://ollama.com) — run LLMs on your own machine
- [DeepEval](https://github.com/confident-ai/deepeval), [RAGAS](https://github.com/explodinggradients/ragas), [Promptfoo](https://www.promptfoo.dev) — the tools we'll use
- Full resource list: [resources.md](resources.md)

---

> *"AI is moving fast. The question is — will you trust it blindly, or will you be the one validating it?"*

Welcome to the course. Let's build AI we can trust.
