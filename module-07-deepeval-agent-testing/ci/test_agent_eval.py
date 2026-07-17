# test_agent_eval.py
# CI-only: evaluates the eval_dataset.json produced by generate_eval_dataset.py
# against all 4 of module 7's DeepEval agent metrics. The agent under test is
# trip_agent, which chains three MCP tools (geocode -> get_weather ->
# suggest_packing) per query.
# Run with: pytest test_agent_eval.py -v   (cwd = this ci/ folder)

import json
import sys
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import (
    ArgumentCorrectnessMetric,
    StepEfficiencyMetric,
    TaskCompletionMetric,
    ToolCorrectnessMetric,
)
from deepeval.test_case import LLMTestCase, ToolCall

TRIP_AGENT_DIR = Path(__file__).resolve().parent.parent / "trip_agent"
sys.path.insert(0, str(TRIP_AGENT_DIR))

from agent import AgentResponse, ToolCallRecord, attach_trace  # noqa: E402

from judge_model import azure_judge_model  # noqa: E402

TASK_DESCRIPTION = (
    "Answer 'what should I pack for a trip to <place>?' by looking up the destination's "
    "coordinates, fetching its forecast, and returning a packing list grounded in that forecast."
)

task_completion_metric = TaskCompletionMetric(task=TASK_DESCRIPTION, threshold=0.7, model=azure_judge_model)
# NOTE: no evaluation_params=[ToolCallParams.INPUT_PARAMETERS] here. This is a
# multi-tool chain where the intermediate arguments (lat/lon, temps) are
# dynamic — produced by an earlier tool's output, not fixed ground truth. So
# ToolCorrectnessMetric checks the *set of tools called* (was the full
# geocode -> get_weather -> suggest_packing chain used), and ArgumentCorrectnessMetric
# (LLM-judged) handles whether the arguments — especially the destination — were right.
tool_correctness_metric = ToolCorrectnessMetric(threshold=0.7, model=azure_judge_model)
argument_correctness_metric = ArgumentCorrectnessMetric(threshold=0.7, model=azure_judge_model)
step_efficiency_metric = StepEfficiencyMetric(threshold=0.7, model=azure_judge_model)

with open("eval_dataset.json", "r") as f:
    raw_cases = [c for c in json.load(f) if not c.get("is_hard_negative")]


def _to_test_case(case: dict) -> LLMTestCase:
    tools_called = [
        ToolCall(name=tc["name"], input_parameters=tc["input_parameters"], output=tc["output"])
        for tc in case["tools_called"]
    ]
    test_case = LLMTestCase(
        input=case["input"],
        actual_output=case["actual_output"],
        tools_called=tools_called,
        expected_tools=[ToolCall(name=name) for name in case["expected_tools"]],
    )
    # StepEfficiencyMetric reads test_case._trace_dict — see trip_agent/agent.py:attach_trace.
    agent_response = AgentResponse(
        output=case["actual_output"],
        tools_called=[
            ToolCallRecord(name=tc["name"], input_parameters=tc["input_parameters"], output=tc["output"])
            for tc in case["tools_called"]
        ],
    )
    attach_trace(test_case, case["input"], agent_response)
    return test_case


test_cases = [(_to_test_case(c), c["category"], c["failure_mode"]) for c in raw_cases]
test_ids = [c["id"] for c in raw_cases]


@pytest.mark.parametrize("test_case,category,failure_mode", test_cases, ids=test_ids)
def test_agent_behavior(test_case, category, failure_mode):
    # run_async=False: assert_test's default fires all 4 metrics' judge calls
    # concurrently (max_concurrent=100), which bursts past the shared training
    # Azure deployment's rate limit. Sequential is slower but measures the same.
    assert_test(
        test_case=test_case,
        metrics=[
            task_completion_metric,
            tool_correctness_metric,
            argument_correctness_metric,
            step_efficiency_metric,
        ],
        run_async=False,
    )
