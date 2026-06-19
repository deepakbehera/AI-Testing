from utils import get_response_from_rag
from deepeval.test_case import LLMTestCase
import json

#--------- Golden Dataset ---------
print("Creating Golden Data for evaluation...")
with open("golden_dataset.json", "r") as f:
    test_cases = [LLMTestCase(input=test_case["input"], expected_output=test_case["expected_output"]) for test_case in json.load(f)]

#---------- Get Response from RAG ---------
print("Getting responses from RAG for the test cases and building eval dataset...")
eval_dataset = []

for test_case in test_cases:
    print(f"Processing query: {test_case.input}")
    response = get_response_from_rag(test_case.input)
    eval_dataset.append(LLMTestCase(
        input=test_case.input,
        expected_output=test_case.expected_output,
        actual_output=response["answer"]    ))

print("Eval dataset built successfully!")

with open("eval_dataset.json", "w") as f:
    json.dump([test_case.__dict__ for test_case in eval_dataset], f, indent=4)