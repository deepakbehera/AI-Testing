# judge_model.py
# CI-only: the RAGAS judge LLM + judge embeddings, shared by every metric in this
# suite. RAGAS needs both an LLM (faithfulness/answer_relevancy/context_precision/
# context_recall judgments) AND an embeddings model (semantic similarity inside
# answer_relevancy) -- one more moving part than DeepEval, where the judge LLM
# alone was enough (see Module 4's judge_model.py). Same PROVIDER switch and same
# Azure resource as Module 4's ci/judge_model.py and ci/generate_eval_dataset.py.

import os

import instructor
import tenacity
from dotenv import load_dotenv
from openai import AsyncOpenAI, BadRequestError
from ragas.embeddings import OpenAIEmbeddings
from ragas.llms import InstructorLLM

load_dotenv()

PROVIDER = os.getenv("PROVIDER", "azure").lower()

if PROVIDER == "azure":
    raw_client = AsyncOpenAI(
        base_url=os.getenv("AZURE_OPENAI_ENDPOINT_C"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
    )
    embed_client = raw_client
    llm_model = os.getenv("AZURE_OPENAI_DEPLOYMENT", "Phi-4-mini-instruct")
    embed_model = os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
    # Mode.JSON_SCHEMA, not the instructor default (TOOLS/function-calling) -- the
    # non-OpenAI models deployed on this Azure resource (Phi, DeepSeek) don't reliably
    # emit OpenAI-style tool calls for RAGAS's more complex output schemas (e.g.
    # faithfulness's per-statement NLI breakdown); they abort instead. Same fix the
    # Ollama branch below already needed.
    instructor_client = instructor.from_openai(raw_client, mode=instructor.Mode.JSON_SCHEMA)
elif PROVIDER == "openai":
    raw_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    embed_client = raw_client
    llm_model = os.getenv("DEMO_MODEL", "gpt-4o-mini")
    embed_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    instructor_client = instructor.from_openai(raw_client)
else:  # ollama
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    raw_client = AsyncOpenAI(base_url=ollama_url, api_key="ollama")
    embed_client = raw_client
    llm_model = os.getenv("DEMO_MODEL", "llama3.2:3b")
    embed_model = os.getenv("OLLAMA_EMBED_MODEL", "all-minilm")
    # Mode.JSON_SCHEMA lets Ollama enforce the output schema at the grammar level --
    # without it, small local models echo the schema description instead of filling it in.
    instructor_client = instructor.from_openai(raw_client, mode=instructor.Mode.JSON_SCHEMA)

judge_llm = InstructorLLM(client=instructor_client, model=llm_model, provider="openai")
judge_embeddings = OpenAIEmbeddings(client=embed_client, model=embed_model)

# The Azure AI Foundry gateway intermittently returns a transient "unknown_model"
# 400 for an embedding deployment that does exist (confirmed in the portal) --
# a different case fails each run, which points to backend routing/propagation
# lag rather than a real config error. Retry a few times before giving up.
_create_embedding = embed_client.embeddings.create


@tenacity.retry(
    retry=tenacity.retry_if_exception_type(BadRequestError),
    wait=tenacity.wait_fixed(2),
    stop=tenacity.stop_after_attempt(4),
    reraise=True,
)
async def _create_embedding_with_retry(*args, **kwargs):
    return await _create_embedding(*args, **kwargs)


embed_client.embeddings.create = _create_embedding_with_retry
