#!/usr/bin/env python3
# cli.py
# Two ways to drive the trip agent:
#
#   Interactive chat (multi-turn) -- just run it with no argument:
#       python cli.py
#     Type questions at the "You:" prompt; type 'exit' or Ctrl+D to quit.
#     Each turn spins up the MCP server, chains geocode -> get_weather ->
#     suggest_packing, and (if LangSmith is on) becomes its own trace.
#
#   One-shot -- pass the question as an argument:
#       python cli.py "What should I pack for a 3-day trip to Reykjavik?"
#
# With LANGSMITH_TRACING=true + a LANGSMITH_API_KEY in .env, every turn shows up
# in the LangSmith UI as a `trip_agent` trace with the MCP tool calls nested under it.

import asyncio
import json
import sys

from agent import run_agent


def _flush_langsmith() -> None:
    """Force any buffered LangSmith traces to send before returning — otherwise a
    quick turn can finish before the background sender flushes and the trace
    never appears in the UI."""
    try:
        from langsmith import utils as ls_utils
        from langsmith.run_trees import get_cached_client

        if ls_utils.tracing_is_enabled():
            get_cached_client().flush()
            print("[LangSmith] trace flushed — check your project in the LangSmith UI.")
    except Exception as exc:  # never let tracing issues break the CLI
        print(f"[LangSmith] flush skipped: {exc}")


def _print_result(response) -> None:
    print(f"\nAgent: {response.output}\n")
    print("Tool calls this turn:")
    for i, tc in enumerate(response.tools_called, 1):
        print(f"  {i}. {tc.name}({tc.input_parameters})")
    print()


async def _one_shot(query: str) -> None:
    response = await run_agent(query, verbose=True)
    _print_result(response)
    _flush_langsmith()


async def _chat() -> None:
    print("Trip agent — ask about what to pack for a trip. Type 'exit' or Ctrl+D to quit.\n")
    while True:
        try:
            query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if query.lower() in ("exit", "quit"):
            print("Bye!")
            break
        if not query:
            continue
        response = await run_agent(query, verbose=True)
        _print_result(response)
        _flush_langsmith()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        asyncio.run(_one_shot(" ".join(sys.argv[1:])))
    else:
        asyncio.run(_chat())
