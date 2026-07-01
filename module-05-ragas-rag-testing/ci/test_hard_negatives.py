# test_hard_negatives.py
# CI-only: metric-sensitivity sanity check, same idea as Module 4 Day 4's testing
# mindset. Hard-negative rows in golden_dataset.json carry a pre-baked (deliberately
# wrong) response and declare which metric (`sensitivity_metric`) should catch it --
# faithfulness for generation failures, context_precision/context_recall for
# retrieval failures. If a hard negative's declared metric doesn't score below
# threshold, that metric isn't sensitive enough.
# Run with: pytest test_hard_negatives.py -v   (cwd = this ci/ folder)

import asyncio
import json

import pytest
from ragas.metrics.collections import AnswerRelevancy, ContextPrecision, ContextRecall, Faithfulness

from judge_model import judge_embeddings, judge_llm

THRESHOLD = 0.7

METRICS = {
    "faithfulness": Faithfulness(llm=judge_llm),
    "answer_relevancy": AnswerRelevancy(llm=judge_llm, embeddings=judge_embeddings),
    "context_precision": ContextPrecision(llm=judge_llm),
    "context_recall": ContextRecall(llm=judge_llm),
}


def _score(metric_name: str, case: dict) -> float:
    metric = METRICS[metric_name]
    if metric_name == "answer_relevancy":
        coro = metric.ascore(user_input=case["user_input"], response=case["response"])
    elif metric_name == "faithfulness":
        coro = metric.ascore(
            user_input=case["user_input"],
            response=case["response"],
            retrieved_contexts=case["retrieved_contexts"],
        )
    else:  # context_precision / context_recall
        coro = metric.ascore(
            user_input=case["user_input"],
            reference=case["reference"],
            retrieved_contexts=case["retrieved_contexts"],
        )
    return asyncio.run(coro).value


with open("eval_dataset.json", "r") as f:
    raw_cases = [c for c in json.load(f) if c.get("is_hard_negative")]

test_ids = [c["id"] for c in raw_cases]


@pytest.mark.parametrize("case", raw_cases, ids=test_ids)
def test_metric_catches_hard_negative(case):
    metric_name = case["sensitivity_metric"]
    score = _score(metric_name, case)
    assert score < THRESHOLD, (
        f"{metric_name}={score:.2f} did not catch hard negative {case['id']} "
        f"(scored >= {THRESHOLD} on a deliberately corrupted case)"
    )
