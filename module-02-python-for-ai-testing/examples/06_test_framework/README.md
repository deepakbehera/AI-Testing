# Mini Test Framework

A small but complete pytest project structure. This is the shape every team's
AI test suite eventually takes.

```
test_framework/
├── conftest.py                 # shared fixtures: llm_client, golden_prompts, assert_response
├── data/
│   └── golden_prompts.json     # the test dataset
└── tests/
    ├── test_golden_suite.py    # one test per golden case (parametrized)
    └── test_latency.py         # performance-focused checks
```

## Run it

From this directory:

```bash
# First-time setup (from the module root)
cd ../..
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Back into the framework folder
cd examples/test_framework

# All tests
pytest -v

# Just correctness
pytest tests/test_golden_suite.py -v

# With HTML report
pytest --html=report.html --self-contained-html

# In parallel (massive speed-up for LLM suites)
pytest -n auto

# Only tests matching a pattern
pytest -v -k "refusal"
```

## What to notice

- `conftest.py` is magic — pytest finds it, the fixtures become available automatically.
- `test_golden_suite.py` uses `pytest_generate_tests` to build one test per JSON entry. Add a new case to `data/golden_prompts.json` and it appears as a new test with no code changes.
- Failing assertions print the case id + response preview, so when something regresses you can spot it fast.

## Extend

Exercise ideas (see `exercises/test_framework_exercise.md`):
1. Add a test module `test_formatting.py` checking that responses don't contain Markdown code fences.
2. Add a new case to `golden_prompts.json` and watch it appear in the run.
3. Add a session-scoped fixture that opens a log file and writes every prompt/response pair into it.
