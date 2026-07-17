# trip_provider.py
# A promptfoo *custom Python provider* that wraps the Module 7 trip agent so
# promptfoo can send it prompts and score its answers.
#
# promptfoo calls `call_api(prompt, options, context)` for every test row and
# expects back a dict with an "output" key. Here, `prompt` is the user's
# question/attack, and we run it through the real trip agent (geocode ->
# get_weather -> suggest_packing over MCP) and return the agent's final answer.
#
# Reference it from a promptfoo config as:
#     providers:
#       - id: file://trip_provider.py
#
# IMPORTANT: promptfoo runs this file with whatever `python` it finds. Point it
# at the project venv (which has mcp/openai/httpx/etc.):
#     export PROMPTFOO_PYTHON=../../.venv/bin/python   # from this examples/ dir
#
# THE AGENT KEEPS ITS OWN MODEL. We do NOT override the agent's provider here:
# it runs on whatever Module 7's trip_agent/.env is configured for (Azure
# DeepSeek in this course setup) — a capable model that can actually drive the
# geocode -> get_weather -> suggest_packing tool chain. promptfoo uses a cheap
# local *Ollama* model only as the JUDGE for llm-rubric assertions (set in the
# config's `defaultTest.options.provider`). Capable agent, free local grader.
# The agent's MCP tools hit the free open-meteo.com API (no keys).

import asyncio
import os
import sys
from pathlib import Path

# Keep LangSmith tracing quiet unless the agent's own .env explicitly turns it on.
os.environ.setdefault("LANGSMITH_TRACING", "false")

# --- Make the Module 7 trip agent importable ------------------------------------
# This file: <root>/module-08-adversarial-red-teaming/examples/trip_provider.py
# parents[2] is the repo root; the trip agent lives under Module 7.
_ROOT = Path(__file__).resolve().parents[2]
_TRIP_AGENT_DIR = _ROOT / "module-07-deepeval-agent-testing" / "trip_agent"
if str(_TRIP_AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(_TRIP_AGENT_DIR))

from agent import run_agent  # noqa: E402  (import after sys.path/env setup)


def call_api(prompt, options, context):
    """promptfoo entry point. Runs one user message through the trip agent.

    Args:
        prompt:   The rendered user message (a string) for this test row.
        options:  Provider options from the YAML; `options["config"]` holds any
                  `config:` block set on the provider (unused here).
        context:  Test metadata (vars, etc.) — unused here.

    Returns:
        dict with "output" (the agent's answer). We also stash the tool names the
        agent called under metadata, so assertions or the web UI can inspect them.
    """
    try:
        result = asyncio.run(run_agent(prompt))
    except BaseException as exc:  # surface failures to promptfoo instead of crashing the run
        # The MCP tool loop runs inside an anyio TaskGroup, so real errors arrive
        # wrapped in an ExceptionGroup. Unwrap to the innermost cause.
        inner = exc
        while isinstance(inner, BaseExceptionGroup) and inner.exceptions:
            inner = inner.exceptions[0]
        text = str(inner)
        # Defense in depth: the model provider's OWN safety layer (e.g. Azure's
        # content filter) can block an attack before the agent ever answers. That
        # is a *resisted* attack, not a test failure — return it as an output so
        # assertions still run and the row reads as a clean pass.
        if "content_filter" in text:
            return {"output": "[request blocked by the model provider's content filter]"}
        return {"error": f"{type(inner).__name__}: {inner}"}

    return {
        "output": result.output,
        "metadata": {"tools_called": [tc.name for tc in result.tools_called]},
    }


# Sanity-check the provider without promptfoo (run with the venv python):
#   python trip_provider.py "What should I pack for Reykjavik in January?"
if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "What should I pack for Reykjavik in January?"
    print(call_api(q, {"config": {}}, {}))
