import pytest

# ── Simple parametrize ───────────────────────────────────────────────────────
@pytest.mark.parametrize("temperature, expected_label", [
    (0.0,  "deterministic"),
    (0.2,  "deterministic"),
    (0.5,  "balanced"),
    (0.79, "balanced"),
    (0.8,  "creative"),
    (1.5,  "creative"),
])
def test_temperature_classification(temperature, expected_label):
    def classify(t: float) -> str:
        if t < 0.3: return "deterministic"
        if t < 0.8: return "balanced"
        return "creative"
    assert classify(temperature) == expected_label


# ── Multiple parameters ──────────────────────────────────────────────────────
@pytest.mark.parametrize("response, keyword, should_pass", [
    ("Paris is the capital of France",     "Paris",  True),
    ("Lyon is a city in France",           "Paris",  False),
    ("Attention Is All You Need",          "attention", True),
    ("No relevant content here",           "transformer", False),
])
def test_keyword_presence(response: str, keyword: str, should_pass: bool):
    result = keyword.lower() in response.lower()
    assert result == should_pass


# ── Parametrize with IDs — cleaner test names ────────────────────────────────
@pytest.mark.parametrize("prompt, must_contain", [
    pytest.param("What is 10 × 10?",        "100",     id="multiplication"),
    pytest.param("What is the square root of 144?", "12",  id="square_root"),
    pytest.param("What is 2 to the power of 8?",   "256", id="exponent"),
], ids=None)  # ids param already set in pytest.param above
def test_math_prompts(prompt, must_contain):
    # Simulated model response — in Day 6 we'll use a real model
    simulated_answers = {
        "What is 10 × 10?": "The answer is 100.",
        "What is the square root of 144?": "The square root of 144 is 12.",
        "What is 2 to the power of 8?": "2^8 = 256.",
    }
    response = simulated_answers[prompt]
    assert must_contain in response, f"Expected {must_contain!r} in {response!r}"
