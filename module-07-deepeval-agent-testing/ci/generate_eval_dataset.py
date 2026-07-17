# generate_eval_dataset.py
# CI-only: builds eval_dataset.json by calling the live trip_agent, which talks
# to the local MCP server (../trip_mcp_server/server.py) over stdio and chains
# geocode -> get_weather -> suggest_packing per query.
# Normal rows call the agent for real; hard-negative rows carry a pre-baked
# (deliberately wrong) actual_output/tools_called and are not re-run.
# Run with: python generate_eval_dataset.py   (cwd = this ci/ folder)

import asyncio
import json
import sys
from pathlib import Path

TRIP_AGENT_DIR = Path(__file__).resolve().parent.parent / "trip_agent"
sys.path.insert(0, str(TRIP_AGENT_DIR))

from agent import run_agent  # noqa: E402

print("Loading golden dataset...")
with open("golden_dataset.json", "r") as f:
    golden_cases = json.load(f)

print(f"Building eval dataset for {len(golden_cases)} golden cases...")
eval_dataset = []
for case in golden_cases:
    if case.get("is_hard_negative"):
        print(f"  -> [{case['category']}/{case['failure_mode']}] {case['id']} (pre-baked, skipping live agent call)")
        actual_output = case["actual_output"]
        tools_called = case["tools_called"]
    else:
        print(f"  -> [{case['category']}/{case['failure_mode']}] {case['id']}")
        response = asyncio.run(run_agent(case["input"]))
        actual_output = response.output
        tools_called = [
            {"name": tc.name, "input_parameters": tc.input_parameters, "output": tc.output}
            for tc in response.tools_called
        ]

    eval_dataset.append({
        "id": case["id"],
        "category": case["category"],
        "failure_mode": case["failure_mode"],
        "is_hard_negative": case.get("is_hard_negative", False),
        "target_metric": case.get("target_metric"),
        "input": case["input"],
        "expected_place": case["expected_place"],
        "expected_tools": case["expected_tools"],
        "actual_output": actual_output,
        "tools_called": tools_called,
    })

with open("eval_dataset.json", "w") as f:
    json.dump(eval_dataset, f, indent=2)

print(f"Wrote eval_dataset.json with {len(eval_dataset)} cases.")
