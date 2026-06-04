"""
Separate test module for latency / performance checks.

Shows that you can split tests across multiple files and pytest
will collect them together. Keep concerns separate — `test_golden_suite`
is about correctness, `test_latency` is about performance.
"""

import pytest


LATENCY_BUDGET_SECONDS = 30.0


@pytest.mark.parametrize("prompt", [
    "Hello",
    "What is Python?",
    "Write a one-line poem about testing.",
])
def test_latency_under_budget(llm_client, prompt):
    resp = llm_client.generate(prompt)
    assert resp.latency_seconds < LATENCY_BUDGET_SECONDS, (
        f"latency {resp.latency_seconds:.2f}s exceeded budget of "
        f"{LATENCY_BUDGET_SECONDS}s for prompt {prompt!r}"
    )


def test_response_is_not_empty(llm_client):
    resp = llm_client.generate("Say one word.")
    assert resp.text.strip(), "model returned an empty response"
