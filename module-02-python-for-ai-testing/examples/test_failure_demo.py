# See what a FAILING assertion looks like — pytest shows both sides
def test_intentional_failure():
    actual = "strawberry".count("r")
    expected = 2   # Wrong — there are 3 r's
    assert actual == expected   # pytest will show: assert 3 == 2
