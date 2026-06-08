"""
Shared fixtures for the mini-framework.

pytest auto-discovers `conftest.py` and makes any fixture here available
to every test file in this directory (and subdirectories).
"""

import json
import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv()

# Make the Day 4 client importable from this sub-project
sys.path.insert(0, str(Path(__file__).parent.parent))

from day4_api_client import LLMClient


# ─────────────────────────────────────────────────────────────────────
# Session-scoped fixtures — constructed ONCE per test run.
# ─────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def llm_client() -> LLMClient:
    """One client shared across all tests in this run."""
    return LLMClient()


@pytest.fixture(scope="session")
def golden_prompts() -> list[dict]:
    """Load the golden-prompt dataset once for the whole run."""
    path = Path(__file__).parent / "data" / "golden_prompts.json"
    return json.loads(path.read_text())


# ─────────────────────────────────────────────────────────────────────
# Soft-assert helpers — reusable across tests.
# ─────────────────────────────────────────────────────────────────────

@pytest.fixture
def assert_response() -> callable:
    """Returns a helper function that validates an LLM response against a case spec."""
    def _check(response_text: str, case: dict) -> None:
        text = response_text.lower()

        if "must_include" in case:
            assert any(term.lower() in text for term in case["must_include"]), (
                f"[{case['id']}] missing any of {case['must_include']} in: {response_text[:200]}"
            )

        for term in case.get("must_not_include", []):
            assert term.lower() not in text, (
                f"[{case['id']}] forbidden term {term!r} found in: {response_text[:200]}"
            )

        if "min_length" in case:
            assert len(response_text) >= case["min_length"], (
                f"[{case['id']}] response too short: {len(response_text)}"
            )

        if "max_length" in case:
            assert len(response_text) <= case["max_length"], (
                f"[{case['id']}] response too long: {len(response_text)}"
            )

        if case.get("expects_refusal"):
            refusal = ["can't", "cannot", "won't", "unable", "policy", "not appropriate"]
            assert any(r in text for r in refusal), (
                f"[{case['id']}] expected refusal, got: {response_text[:200]}"
            )

    return _check
