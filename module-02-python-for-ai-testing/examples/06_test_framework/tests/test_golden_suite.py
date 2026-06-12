"""
Golden-suite tests — one test case per entry in data/golden_prompts.json.

Run from `examples/test_framework/`:
    pytest tests/ -v
    pytest tests/ -v --html=report.html --self-contained-html
    pytest tests/ -n auto                    # parallel
"""

import pytest


def _ids(cases):
    return [c["id"] for c in cases]


def test_golden_dataset_loads(golden_prompts):
    """Sanity check: our dataset loads and has cases."""
    assert len(golden_prompts) > 0
    for case in golden_prompts:
        assert "id" in case and "prompt" in case


def test_golden_ids_unique(golden_prompts):
    ids = [c["id"] for c in golden_prompts]
    assert len(ids) == len(set(ids)), "duplicate test-case IDs found"


@pytest.fixture(params=[])
def _lazy_cases():
    return []


def pytest_generate_tests(metafunc):
    """Dynamically parametrize test_golden_case with cases loaded from JSON."""
    if "case" in metafunc.fixturenames:
        import json
        from pathlib import Path
        path = Path(__file__).parent.parent / "data" / "golden_prompts.json"
        cases = json.loads(path.read_text())
        metafunc.parametrize("case", cases, ids=[c["id"] for c in cases])


def test_golden_case(case, llm_client, assert_response):
    """One test per entry in golden_prompts.json — fully parametrized."""
    resp = llm_client.generate(case["prompt"])
    assert_response(resp.text, case)
