# test_llm_eval.py
# CI-only: evaluates the eval_dataset.json produced by generate_eval_dataset.py.
# Run with: pytest test_llm_eval.py -v   (cwd = this ci/ folder)

import json

import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from judge_model import azure_judge_model

answer_relevancy_metric = AnswerRelevancyMetric(
    threshold=0.7, model=azure_judge_model, include_reason=True, async_mode=False
)
faithfulness_metric = FaithfulnessMetric(
    threshold=0.7, model=azure_judge_model, include_reason=True, async_mode=False
)
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
    raw_cases = [c for c in json.load(f) if not c.get("is_hard_negative")]


def _to_test_case(case: dict) -> LLMTestCase:
    return LLMTestCase(
        input=case["input"],
        expected_output=case["expected_output"],
        actual_output=case["actual_output"],
        retrieval_context=case.get("context"),
    )


test_cases = [(_to_test_case(c), c["category"], c["failure_mode"]) for c in raw_cases]
test_ids = [c["id"] for c in raw_cases]


@pytest.mark.parametrize("test_case,category,failure_mode", test_cases, ids=test_ids)
def test_llm_answer_quality(test_case, category, failure_mode):
    metrics = [answer_relevancy_metric, correctness_metric]
    if test_case.retrieval_context:
        metrics.append(faithfulness_metric)
    assert_test(test_case=test_case, metrics=metrics)
