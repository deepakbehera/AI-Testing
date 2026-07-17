# judge_model.py
# CI-only: the DeepEval judge model, shared by every metric in this suite.
# DeepEval defaults its judge to OpenAI unless told otherwise — we're testing
# an Azure-deployed agent, so the judge must be explicit about Azure too,
# reading the same AZURE_* env vars as modules 4/5's CI suites.

from deepeval.models import AzureOpenAIModel

azure_judge_model = AzureOpenAIModel()
