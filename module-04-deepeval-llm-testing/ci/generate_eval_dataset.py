# generate_eval_dataset.py
# CI-only: builds eval_dataset.json by calling the LLM directly.
# No deployed app/RAG server required — we only have the model, not the app.
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
    MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
else:  # ollama
    client = OpenAI(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        api_key="ollama",
    )
    MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")


def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def build_prompt(case: dict) -> str:
    """RAG-style cases carry their own context — fold it into the prompt
    inline since there's no retrieval service running in CI."""
    if case.get("context"):
        context_block = "\n".join(case["context"])
        return f"Context:\n{context_block}\n\nQuestion: {case['input']}\n\nAnswer using only the context above."
    return case["input"]


print(f"Loading golden dataset (provider={PROVIDER}, model={MODEL})...")
with open("golden_dataset.json", "r") as f:
    golden_cases = json.load(f)

print(f"Building eval dataset for {len(golden_cases)} golden cases...")
eval_dataset = []
for case in golden_cases:
    # Hard-negative rows already carry a pre-baked (deliberately wrong)
    # actual_output — they exist to sanity-check metric sensitivity offline,
    # not to be re-answered by a live model call.
    if "actual_output" in case:
        print(f"  -> [{case['category']}/{case['failure_mode']}] {case['id']} (pre-baked, skipping LLM call)")
        actual_output = case["actual_output"]
    else:
        print(f"  -> [{case['category']}/{case['failure_mode']}] {case['id']}")
        actual_output = call_llm(build_prompt(case))
    eval_dataset.append({
        "id": case["id"],
        "category": case["category"],
        "failure_mode": case["failure_mode"],
        "is_hard_negative": case.get("is_hard_negative", False),
        "input": case["input"],
        "expected_output": case["expected_output"],
        "actual_output": actual_output,
        "context": case.get("context"),
    })

with open("eval_dataset.json", "w") as f:
    json.dump(eval_dataset, f, indent=2)

print(f"Wrote eval_dataset.json with {len(eval_dataset)} cases.")
