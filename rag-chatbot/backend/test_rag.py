#!/usr/bin/env python3
"""Quick test to verify the backend works end-to-end."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from rag_engine import create_engine

engine = create_engine()
print(f"✅ Engine created (LLM: {engine.llm_model}, Embed: {engine.embed_model_name})")

# Test document ingestion
test_content = "Paris is the capital of France. The Eiffel Tower is located in Paris."
test_path = "/tmp/_rag_test_doc.txt"
with open(test_path, "w") as f:
    f.write(test_content)

doc_id = engine.ingest_file(test_path)
os.unlink(test_path)
print(f"✅ Ingested test doc: {doc_id}")

# Test retrieval
results = engine.retrieve("What is the capital of France?", top_k=3)
print(f"✅ Retrieved {len(results)} chunks")
for r in results:
    print(f"   → {r[:80]}...")

# Test chat
answer, sources = engine.chat("What is the capital of France?", top_k=3)
print(f"✅ Chat answer: {answer[:120]}...")
print(f"✅ Sources: {len(sources)} chunks")

# Cleanup
engine.clear_all()
print("✅ Cleanup complete")
print("\n🎉 All tests passed!")
