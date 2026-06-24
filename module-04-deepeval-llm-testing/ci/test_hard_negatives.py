# test_hard_negatives.py
# CI-only: metric-sensitivity sanity check from Module 4 Day 4's testing mindset.
# Hard-negative rows in golden_dataset.json carry a pre-baked (deliberately
# wrong) actual_output — they must FAIL the same metric the matching normal
# row passes in test_llm_eval.py. If a hard negative ever passes, the metric
# isn't sensitive enough.
# Run with: pytest test_hard_negatives.py -v   (cwd = this ci/ folder)

import json

import pytest
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from judge_model import azure_judge_model

correctness_metric = GEval(
    name="Correctness",
    criteria=(
        "Determine whether the actual output is factually consistent with the "
        "expected output and does not introduce facts that contradict it."
    ),
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    threshold=0.7,
    model=azure_judge_model,
)

with open("eval_dataset.json", "r") as f:
    raw_cases = [c for c in json.load(f) if c.get("is_hard_negative")]


def _to_test_case(case: dict) -> LLMTestCase:
    return LLMTestCase(
        input=case["input"],
        expected_output=case["expected_output"],
        actual_output=case["actual_output"],
        retrieval_context=case.get("context"),
    )


test_cases = [_to_test_case(c) for c in raw_cases]
test_ids = [c["id"] for c in raw_cases]


@pytest.mark.parametrize("test_case", test_cases, ids=test_ids)
def test_metric_catches_hard_negative(test_case):
    # If this does NOT raise, the metric is not sensitive enough to catch
    # the deliberately corrupted answer — that's the actual bug.
    with pytest.raises(AssertionError):
        assert_test(test_case=test_case, metrics=[correctness_metric])
