import pytest

# ── Simple fixture ───────────────────────────────────────────────────────────
@pytest.fixture
def sample_response():
    """A realistic LLM response string for testing."""
    return (
        "The transformer architecture, introduced in the paper 'Attention Is All "
        "You Need' (2017), uses self-attention mechanisms to process sequential "
        "data. Unlike RNNs, transformers process all tokens in parallel, enabling "
        "much faster training and longer context understanding."
    )

@pytest.fixture
def response_config():
    """Default behavioral constraints for response testing."""
    return {"min_length": 50, "max_length": 1000, "required_keywords": ["attention"]}


# Tests that use the fixtures — pytest injects them by name
def test_response_not_empty(sample_response):
    assert len(sample_response) > 0

def test_response_length(sample_response, response_config):
    assert len(sample_response) >= response_config["min_length"]
    assert len(sample_response) <= response_config["max_length"]

def test_response_contains_keyword(sample_response, response_config):
    for kw in response_config["required_keywords"]:
        assert kw.lower() in sample_response.lower(), f"Missing keyword: {kw!r}"

def test_response_no_refusal(sample_response):
    refusal_signals = ["i can't", "i cannot", "i'm not able"]
    for sig in refusal_signals:
        assert sig not in sample_response.lower()


# ── Fixture that yields (teardown) ───────────────────────────────────────────
@pytest.fixture
def temp_file(tmp_path):
    """Create a temp JSON file, yield the path, clean up after."""
    import json
    f = tmp_path / "test_data.json"
    f.write_text(json.dumps([{"id": 1, "score": 0.9}]))
    yield f                   # test runs here
    # cleanup code goes after yield — runs even if test fails
    # f.unlink()  # tmp_path is auto-cleaned by pytest — just for illustration

def test_file_has_content(temp_file):
    import json
    data = json.loads(temp_file.read_text())
    assert len(data) == 1
    assert data[0]["score"] == 0.9
