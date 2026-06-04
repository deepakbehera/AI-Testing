# pytest discovers this file automatically

# Basic assertions — the whole pytest vocabulary
def test_equality():
    assert 2 + 2 == 3
    assert "hello".upper() == "HELLO"
    assert len([1, 2, 3]) == 3

def test_membership():
    response = "The transformer uses self-attention."
    assert "attention" in response.lower()
    assert "LSTM" not in response

def test_types():
    score = 0.87
    assert isinstance(score, float)
    assert isinstance(score, (int, float))   # either type is fine
    assert 0.0 <= score <= 1.0               # chained comparison

def test_exceptions():
    import pytest, json
    # Assert that a function raises a specific exception
    with pytest.raises(json.JSONDecodeError):
        json.loads("not valid json")

    with pytest.raises(ZeroDivisionError, match="division by zero"):
        _ = 1 / 0

def test_approximate_equality():
    # Floating-point: never use == for floats
    result = 0.1 + 0.2
    assert abs(result - 0.3) < 1e-9   # tolerance-based
    # OR use pytest.approx:
    import pytest
    assert result == pytest.approx(0.3, abs=1e-9)
