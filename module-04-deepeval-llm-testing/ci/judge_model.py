# judge_model.py
# CI-only: the DeepEval judge model, shared by every metric in this suite.
# DeepEval defaults its judge to OpenAI unless told otherwise — we're testing
# an Azure-deployed model, so the judge must be explicit about Azure too,
# reading the same AZURE_* env vars as the rest of this module.

from deepeval.models import AzureOpenAIModel

azure_judge_model = AzureOpenAIModel()
