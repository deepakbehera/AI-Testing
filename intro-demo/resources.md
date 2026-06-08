# Day 0 — Resources

Links to have handy before and after the demo class.

## Running LLMs locally (used in the demo)
- Ollama — https://ollama.com
- Ollama model library — https://ollama.com/library
- Ollama OpenAI-compatible API docs — https://github.com/ollama/ollama/blob/main/docs/openai.md

Models used in the demo:
- `llama3.2:3b` — Meta's small general-purpose model (default)
- `qwen2.5-coder:3b` — Alibaba's code-focused small model
- `llama3.2:latest` — alias for `llama3.2:3b`

## Cloud providers (fallback + used in later modules)
- OpenAI API docs — https://platform.openai.com/docs
- Anthropic API docs — https://docs.anthropic.com
- `python-dotenv` — https://github.com/theskumar/python-dotenv

## Tools covered later in the course
- DeepEval — https://github.com/confident-ai/deepeval
- RAGAS — https://github.com/explodinggradients/ragas
- Promptfoo — https://www.promptfoo.dev
- LangSmith — https://www.langchain.com/langsmith
- GitHub Actions — https://docs.github.com/en/actions

## Reference reading (mention at the end of the demo)
- OWASP Top 10 for LLM Applications — https://owasp.org/www-project-top-10-for-large-language-model-applications/
- NIST AI Risk Management Framework — https://www.nist.gov/itl/ai-risk-management-framework
- Anthropic "Building effective agents" — https://www.anthropic.com/research

## Sample prompts for the live demo (feel free to swap)
- "Explain blockchain in simple terms."
- "Write a 2-sentence bio for a software tester learning AI."
- "Summarize the difference between AI and machine learning."
- "Who is the current president of Mars?" *(hallucination probe)*
- "List three ways AI systems can fail silently." *(self-aware probe)*

## Setup cheatsheet

```bash
# 1. Start Ollama (in its own terminal, or as a background service)
ollama serve

# 2. Pull the model (one-time, ~2 GB)
ollama pull llama3.2:3b
ollama list                         # verify

# 3. Python env + deps
cd day-00-demo
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. Config (defaults to Ollama — no API key needed)
cp .env.example .env

# 5. Run the demos
python examples/live_demo_same_prompt.py
python examples/simple_automation.py
```

### Switching to OpenAI or Anthropic
Edit `.env`:
```
PROVIDER=openai                     # or "anthropic"
DEMO_MODEL=gpt-4o-mini              # or "claude-sonnet-4-6"
OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
```
No code changes required — both scripts route through the `PROVIDER` env var.
