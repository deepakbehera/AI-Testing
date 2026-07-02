# agent.py
# A real (not stubbed) minimal agentic RAG loop: embedding-similarity retrieval,
# an LLM planner that decides whether to keep retrieving, and an LLM generator
# that writes the final answer -- every decision point is a live model call, not
# a rule-based stand-in. Same PROVIDER switch and Azure resource Module 5's
# CI used. Lives alongside the notebooks (no separate ci/ folder, no pytest
# suite) -- what's new in this module is the agent itself, and that's taught
# interactively in examples/*.ipynb, not re-packaged into a Module 5-shaped
# CI pipeline with different metrics bolted on.

import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import instructor
import tenacity
from dotenv import load_dotenv
from langsmith import traceable
from openai import AsyncOpenAI, BadRequestError
from pydantic import BaseModel

# Anchored to this file's own directory, not the caller's cwd.
load_dotenv(Path(__file__).resolve().parent / ".env")

PROVIDER = os.getenv("PROVIDER", "azure").lower()

if PROVIDER == "azure":
    _client = AsyncOpenAI(
        base_url=os.getenv("AZURE_OPENAI_ENDPOINT_C"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
    )
    _llm_model = os.getenv("AZURE_OPENAI_DEPLOYMENT", "DeepSeek-V3.2")
    _embed_model = os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
    # Mode.JSON_SCHEMA, not the instructor default (TOOLS/function-calling) --
    # the non-OpenAI models on this Azure resource don't reliably emit
    # OpenAI-style tool calls.
    _instructor_client = instructor.from_openai(_client, mode=instructor.Mode.JSON_SCHEMA)
elif PROVIDER == "openai":
    _client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    _llm_model = os.getenv("DEMO_MODEL", "gpt-4o-mini")
    _embed_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    _instructor_client = instructor.from_openai(_client)
else:  # ollama
    _ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    _client = AsyncOpenAI(base_url=_ollama_url, api_key="ollama")
    _llm_model = os.getenv("DEMO_MODEL", "llama3.2:3b")
    _embed_model = os.getenv("OLLAMA_EMBED_MODEL", "all-minilm")
    _instructor_client = instructor.from_openai(_client, mode=instructor.Mode.JSON_SCHEMA)


# ---------------------------------------------------------------------------
#  Corpus -- deliberately requires 2 hops for several questions (a fact about
#  WHICH product/office is current, plus a separate fact that depends on it).
# ---------------------------------------------------------------------------

CORPUS = [
    "WidgetPro 2000 was discontinued in 2023 and replaced by WidgetPro 3000.",
    "WidgetPro 3000's cancellation fee is $0 -- it can be canceled anytime at no charge.",
    "WidgetPro 2000's cancellation fee was $50 before it was discontinued.",
    "Our premium support plan includes 24/7 phone access and a 1-hour response SLA.",
    "TurboMax 5 was renamed to TurboMax Pro in 2024 after a rebranding update.",
    "TurboMax Pro's annual subscription costs $299, unchanged from TurboMax 5's price.",
    "Our headquarters relocated from Austin to Denver in 2022.",
    "The Denver office does not offer walk-in support; all support is online only.",
]


# ---------------------------------------------------------------------------
#  Retrieval -- real embedding similarity, not keyword matching against a dict.
# ---------------------------------------------------------------------------

@tenacity.retry(
    retry=tenacity.retry_if_exception_type(BadRequestError),
    wait=tenacity.wait_fixed(2),
    stop=tenacity.stop_after_attempt(4),
    reraise=True,
)
async def _create_embeddings(texts: List[str]) -> List[List[float]]:
    resp = await _client.embeddings.create(model=_embed_model, input=texts)
    return [d.embedding for d in resp.data]


def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


_corpus_embeddings: Optional[List[List[float]]] = None


@traceable(run_type="retriever")
async def retrieve(query: str, top_k: int = 2) -> List[str]:
    """Real embedding-similarity retrieval over CORPUS."""
    global _corpus_embeddings
    if _corpus_embeddings is None:
        _corpus_embeddings = await _create_embeddings(CORPUS)
    query_emb = (await _create_embeddings([query]))[0]
    scored = sorted(zip(CORPUS, _corpus_embeddings), key=lambda pair: -_cosine(query_emb, pair[1]))
    return [text for text, _ in scored[:top_k]]


# ---------------------------------------------------------------------------
#  Planner -- a real LLM call deciding whether to keep retrieving, not a
#  one-line rule. Structured output via instructor, same library Module 5's
#  RAGAS judge setup uses for its own structured judgments.
# ---------------------------------------------------------------------------

class PlannerDecision(BaseModel):
    enough_info: bool
    reasoning: str
    next_query: str  # ignored once enough_info is True


@traceable(run_type="chain", name="planner")
async def _plan(question: str, facts_so_far: List[str]) -> PlannerDecision:
    facts_block = "\n".join(f"- {f}" for f in facts_so_far) or "(none yet)"
    prompt = (
        "You are the planner in a multi-hop retrieval-augmented QA agent.\n"
        f"User question: {question}\n\n"
        f"Facts retrieved so far:\n{facts_block}\n\n"
        "Decide whether these facts are enough to fully and correctly answer the "
        "question. If not, give the next search query that would retrieve the "
        "missing piece. Never guess at a fact that isn't listed above."
    )
    return await _instructor_client.chat.completions.create(
        model=_llm_model,
        response_model=PlannerDecision,
        messages=[{"role": "user", "content": prompt}],
    )


# ---------------------------------------------------------------------------
#  Generator -- a real LLM call writing the final answer from accumulated facts.
# ---------------------------------------------------------------------------

@traceable(run_type="llm", name="generator")
async def _generate(question: str, facts: List[str], uncertain: bool = False) -> str:
    facts_block = "\n".join(f"- {f}" for f in facts) or "(no facts retrieved)"
    prompt = (
        "Answer the user's question using ONLY the facts below. If the facts "
        "don't contain the answer, say so plainly instead of guessing.\n\n"
        f"Facts:\n{facts_block}\n\nQuestion: {question}\n\nAnswer:"
    )
    if uncertain:
        prompt += (
            "\n\nNote: the planner was not confident these facts fully answer the "
            "question before giving up. If they don't, say what's missing instead "
            "of answering as if they do."
        )
    resp = await _client.chat.completions.create(
        model=_llm_model,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content


# ---------------------------------------------------------------------------
#  The agentic loop itself.
# ---------------------------------------------------------------------------

@dataclass
class AgentResult:
    response: str
    retrieved_contexts: List[str]
    num_hops: int
    hit_max_hops: bool  # True if the planner NEVER confirmed enough_info before hops ran out --
                         # the bounded-loop shape of "infinite retrieval loop" (Day 1's failure-mode table)


@traceable(run_type="chain", name="agentic_rag_loop")
async def agentic_rag(question: str, max_hops: int = 3, verbose: bool = False) -> AgentResult:
    """Real (LLM-planned, embedding-retrieved) multi-hop agentic RAG loop.

    verbose=True prints each hop's retrieved facts and the planner's actual
    reasoning -- useful in a notebook to see a real decision, not a rule.
    """
    facts: List[str] = []
    query = question
    hop = 0
    hit_max_hops = True
    for hop in range(1, max_hops + 1):
        new_facts = await retrieve(query)
        for f in new_facts:
            if f not in facts:
                facts.append(f)
        decision = await _plan(question, facts)
        if verbose:
            print(f"[hop {hop}] query={query!r}")
            print(f"[hop {hop}] retrieved: {new_facts}")
            print(f"[hop {hop}] planner.enough_info={decision.enough_info}  reasoning={decision.reasoning!r}")
            if not decision.enough_info:
                print(f"[hop {hop}] next_query={decision.next_query!r}")
            print()
        if decision.enough_info:
            hit_max_hops = False
            break
        query = decision.next_query
    if hit_max_hops and verbose:
        print(f"[warning] exhausted max_hops={max_hops} without the planner ever confirming enough_info -- "
              f"generating from whatever facts were found anyway.")
    # Be honest with the generator about an unconfirmed stop -- it should hedge
    # rather than confidently answer from facts the planner itself wasn't sure covered the question.
    response = await _generate(question, facts, uncertain=hit_max_hops)
    return AgentResult(response=response, retrieved_contexts=facts, num_hops=hop, hit_max_hops=hit_max_hops)
