# Exercise: Python Setup & Syntax

**Estimated time:** 30–45 minutes

---

## Part A — Setup Verification (10 min)

1. Open a terminal and confirm Python version: `python3 --version` (must be 3.10+).
2. Create and activate a venv for this module:
   ```bash
   cd module-02-python-for-ai-testing
   python3 -m venv .venv
   source .venv/bin/activate    # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Run the notebook: open `examples/python_quickstart.ipynb` in Jupyter or VS Code and run all cells.
4. Confirm all cells execute without errors.

---

## Part B — Coding Tasks (20–25 min)

Create a file `exercises/python_setup_solution.py` with the following:

### Task 1 — Prompt Classifier

Write a function `classify_prompt(prompt: str) -> dict` that returns a dict with:
- `"length_category"`: `"short"` (< 30 chars), `"medium"` (30–200), `"long"` (> 200)
- `"has_question"`: `True` if the prompt ends with `?` or contains a question word (`what`, `why`, `how`, `when`, `where`, `who`, `which`)
- `"word_count"`: integer count of words
- `"has_numbers"`: `True` if the prompt contains any digit

Test data to use:
```python
test_prompts = [
    "Hi",
    "What is a transformer?",
    "Explain the difference between BERT and GPT-2 in detail. Include architecture, training objectives, and typical use cases.",
    "List 3 advantages of using RAG over fine-tuning.",
    "How do I handle rate limiting when calling OpenAI's API 100 times per minute?",
]
```

Print a table of results — one row per prompt.

### Task 2 — Statistics Tracker

Write a function `compute_stats(results: list[dict]) -> dict` that takes a list of `classify_prompt` results and returns:
- `"total"`: total count
- `"short_count"`, `"medium_count"`, `"long_count"`: count per category
- `"questions_pct"`: percentage that are questions (0–100, one decimal place)
- `"avg_word_count"`: average word count (one decimal place)

### Task 3 — Pretty Report

Write a `print_report(prompts, results)` function that prints:
```
PROMPT ANALYSIS REPORT
======================
Total prompts: 5

Length distribution:
  short  : 1  (20.0%)
  medium : 3  (60.0%)
  long   : 1  (20.0%)

Questions: 3 / 5 (60.0%)
Avg words: 12.4

Detail:
  [medium] [question] [words:4 ] What is a transformer?
  [short ] [         ] [words:1 ] Hi
  ...
```

---

## Part C — Bonus (optional, +10 min)

Add a `classify_sentiment_simple(prompt: str) -> str` function that returns `"positive"`, `"negative"`, or `"neutral"` based on keyword matching (no external library):
- Positive: `"great"`, `"good"`, `"help"`, `"explain"`, `"teach"`
- Negative: `"bad"`, `"wrong"`, `"fail"`, `"error"`, `"broken"`
- Neutral: everything else

---

## Self-Check

- [ ] `python3 --version` shows 3.10+
- [ ] venv is active (prompt shows `(.venv)`)
- [ ] All Day 1 notebook cells run without errors
- [ ] `classify_prompt` returns a dict with all 4 keys
- [ ] `compute_stats` handles an empty list without crashing
- [ ] `print_report` output is readable and aligned
- [ ] You understand what each line of your code does

## Share
Post `python_setup_solution.py` in the class channel before Day 2, plus one question you had while writing it.
