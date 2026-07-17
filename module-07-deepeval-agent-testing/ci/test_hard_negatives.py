# test_hard_negatives.py
# CI-only: metric-sensitivity sanity check from Module 4 Day 4's testing mindset.
# Hard-negative rows in golden_dataset.json carry a pre-baked (deliberately
# wrong) actual_output/tools_called — each one must FAIL its declared
# target_metric. If a hard negative ever passes, that metric isn't sensitive
# enough to catch the failure mode it's supposed to catch.
#
# The four failure modes exercised (one per metric):
#   wrong_tool          -> tool_correctness   (chain missing suggest_packing / no tools at all)
#   wrong_argument      -> argument_correctness (geocoded the wrong destination)
#   inefficient_steps   -> step_efficiency    (geocode/get_weather called twice)
#   incomplete_answer   -> task_completion    (refused to help)
# Run with: pytest test_hard_negatives.py -v   (cwd = this ci/ folder)

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

METRICS_BY_NAME = {
    "task_completion": TaskCompletionMetric(task=TASK_DESCRIPTION, threshold=0.7, model=azure_judge_model),
    "tool_correctness": ToolCorrectnessMetric(threshold=0.7, model=azure_judge_model),
    "argument_correctness": ArgumentCorrectnessMetric(threshold=0.7, model=azure_judge_model),
    "step_efficiency": StepEfficiencyMetric(threshold=0.7, model=azure_judge_model),
}

with open("eval_dataset.json", "r") as f:
    raw_cases = [c for c in json.load(f) if c.get("is_hard_negative")]


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
    agent_response = AgentResponse(
        output=case["actual_output"],
        tools_called=[
            ToolCallRecord(name=tc["name"], input_parameters=tc["input_parameters"], output=tc["output"])
            for tc in case["tools_called"]
        ],
    )
    attach_trace(test_case, case["input"], agent_response)
    return test_case


test_cases = [(_to_test_case(c), METRICS_BY_NAME[c["target_metric"]]) for c in raw_cases]
test_ids = [c["id"] for c in raw_cases]


@pytest.mark.parametrize("test_case,metric", test_cases, ids=test_ids)
def test_metric_catches_hard_negative(test_case, metric):
    # If this does NOT raise, the metric is not sensitive enough to catch
    # the deliberately corrupted agent behavior — that's the actual bug.
    # run_async=False: see the comment in test_agent_eval.py.
    with pytest.raises(AssertionError):
        assert_test(test_case=test_case, metrics=[metric], run_async=False)
