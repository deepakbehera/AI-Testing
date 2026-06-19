# we want to connect to the API and build some functions to get response from the application

import requests
import dotenv
import os
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric , AnswerRelevancyMetric
from deepeval import assert_test
import pytest
import json
dotenv.load_dotenv()


#---------- Evaluate the responses using DeepEval Metrics ---------
faithfulness_metric = FaithfulnessMetric(threshold=0.5, include_reason=True, async_mode=False)
answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.5, include_reason=True, async_mode=False)

with open("eval_dataset.json", "r") as f:
    eval_dataset = [LLMTestCase(input=test_case["input"], expected_output=test_case["expected_output"], actual_output=test_case["actual_output"]    ) for test_case in json.load(f)]


@pytest.mark.parametrize("test_case", eval_dataset)
def test_rag_chatbot(test_case):
    assert_test(
        test_case=test_case,
        metrics=[answer_relevancy_metric]
    )