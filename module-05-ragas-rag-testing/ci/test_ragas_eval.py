# test_ragas_eval.py
# CI-only: evaluates the eval_dataset.json produced by generate_eval_dataset.py
# against RAGAS's 4 core metrics. RAGAS has no assert_test() helper like DeepEval --
# each metric is scored (async, via .ascore()) and asserted against a threshold
# by hand.
# Run with: pytest test_ragas_eval.py -v   (cwd = this ci/ folder)

import asyncio
import json

import pytest
from ragas.metrics.collections import AnswerRelevancy, ContextPrecision, ContextRecall, Faithfulness

from judge_model import judge_embeddings, judge_llm

THRESHOLD = 0.7

faithfulness = Faithfulness(llm=judge_llm)
answer_relevancy = AnswerRelevancy(llm=judge_llm, embeddings=judge_embeddings)
context_precision = ContextPrecision(llm=judge_llm)
context_recall = ContextRecall(llm=judge_llm)

with open("eval_dataset.json", "r") as f:
    raw_cases = [c for c in json.load(f) if not c.get("is_hard_negative")]

test_ids = [c["id"] for c in raw_cases]


@pytest.mark.parametrize("case", raw_cases, ids=test_ids)
def test_faithfulness(case):
    score = asyncio.run(faithfulness.ascore(
        user_input=case["user_input"],
        response=case["response"],
        retrieved_contexts=case["retrieved_contexts"],
    )).value
    assert score >= THRESHOLD, f"faithfulness={score:.2f} below {THRESHOLD} for {case['id']}"


@pytest.mark.parametrize("case", raw_cases, ids=test_ids)
def test_answer_relevancy(case):
    score = asyncio.run(answer_relevancy.ascore(
        user_input=case["user_input"],
        response=case["response"],
    )).value
    assert score >= THRESHOLD, f"answer_relevancy={score:.2f} below {THRESHOLD} for {case['id']}"


@pytest.mark.parametrize("case", raw_cases, ids=test_ids)
def test_context_precision(case):
    score = asyncio.run(context_precision.ascore(
        user_input=case["user_input"],
        reference=case["reference"],
        retrieved_contexts=case["retrieved_contexts"],
    )).value
    assert score >= THRESHOLD, f"context_precision={score:.2f} below {THRESHOLD} for {case['id']}"


@pytest.mark.parametrize("case", raw_cases, ids=test_ids)
def test_context_recall(case):
    score = asyncio.run(context_recall.ascore(
        user_input=case["user_input"],
        reference=case["reference"],
        retrieved_contexts=case["retrieved_contexts"],
    )).value
    assert score >= THRESHOLD, f"context_recall={score:.2f} below {THRESHOLD} for {case['id']}"
