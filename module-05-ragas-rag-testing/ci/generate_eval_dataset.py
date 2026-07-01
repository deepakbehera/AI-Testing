# generate_eval_dataset.py
# CI-only: builds eval_dataset.json by calling the generator LLM directly, using the
# hand-authored retrieved_contexts already in golden_dataset.json.
# No deployed rag-chatbot / retriever required -- same "test the model, not the app"
# shortcut Module 4 used, one layer up: retrieval is faked (hand-authored contexts),
# generation is real (a live LLM call).
# Run with: python generate_eval_dataset.py   (cwd = this ci/ folder)

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PROVIDER = os.getenv("PROVIDER", "azure").lower()

if PROVIDER == "azure":
    client = OpenAI(
        base_url=os.getenv("AZURE_OPENAI_ENDPOINT_C"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
    )
    MODEL = os.getenv("AZURE_OPENAI_DEPLOYMENT", "Phi-4-mini-instruct")
elif PROVIDER == "openai":
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    MODEL = os.getenv("DEMO_MODEL", "gpt-4o-mini")
else:  # ollama
    client = OpenAI(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        api_key="ollama",
    )
    MODEL = os.getenv("DEMO_MODEL", "llama3.2:3b")


def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def build_prompt(case: dict) -> str:
    context_block = "\n".join(case["retrieved_contexts"])
    return f"Context:\n{context_block}\n\nQuestion: {case['user_input']}\n\nAnswer using only the context above."


print(f"Loading golden dataset (provider={PROVIDER}, model={MODEL})...")
with open("golden_dataset.json", "r") as f:
    golden_cases = json.load(f)

print(f"Building eval dataset for {len(golden_cases)} golden cases...")
eval_dataset = []
for case in golden_cases:
    # Hard-negative rows already carry a pre-baked (deliberately wrong) response --
    # they exist to sanity-check metric sensitivity offline, not to be re-answered
    # by a live model call.
    if "response" in case:
        print(f"  -> [{case['category']}/{case['failure_mode']}] {case['id']} (pre-baked, skipping LLM call)")
        response = case["response"]
    else:
        print(f"  -> [{case['category']}/{case['failure_mode']}] {case['id']}")
        response = call_llm(build_prompt(case))
    eval_dataset.append({
        "id": case["id"],
        "category": case["category"],
        "failure_mode": case["failure_mode"],
        "is_hard_negative": case.get("is_hard_negative", False),
        "sensitivity_metric": case.get("sensitivity_metric"),
        "user_input": case["user_input"],
        "reference": case["reference"],
        "retrieved_contexts": case["retrieved_contexts"],
        "response": response,
    })

with open("eval_dataset.json", "w") as f:
    json.dump(eval_dataset, f, indent=2)

print(f"Wrote eval_dataset.json with {len(eval_dataset)} cases.")
