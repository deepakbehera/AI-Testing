#!/usr/bin/env python3
# cli.py
# Runs weather_agent.agent.run_agent() in a plain, freshly-started Python
# process and prints the result as one JSON line to stdout.
#
# Why this exists: the Day 1/2 notebooks run inside a Jupyter kernel that has
# nest_asyncio applied (ipykernel loads it to support top-level await). That
# monkey-patches asyncio.run()/BaseEventLoop.run_until_complete() for the
# whole process — including any new thread — which breaks sniffio's
# current_async_library() detection deep inside httpx/openai's anyio-based
# retry logic (AsyncLibraryNotFoundError). Spawning a genuinely separate
# process sidesteps that patch entirely, since it starts with a clean,
# un-patched asyncio.

import asyncio
import json
import sys

from agent import run_agent


async def main() -> None:
    query = sys.argv[1]
    response = await run_agent(query, verbose=False)
    print(json.dumps({
        "output": response.output,
        "tools_called": [
            {"name": tc.name, "input_parameters": tc.input_parameters, "output": tc.output}
            for tc in response.tools_called
        ],
    }))


if __name__ == "__main__":
    asyncio.run(main())
