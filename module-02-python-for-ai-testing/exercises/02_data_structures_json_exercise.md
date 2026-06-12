# Exercise: Data Structures & JSON

**Estimated time:** 30–40 minutes

---

## Part A — JSON Parsing Pipeline (20 min)

Create `exercises/data_structures_solution.py`.

Ask the LLM for a structured JSON description of a **restaurant menu item** (your choice). The JSON must have:
- `name`: string
- `cuisine`: string (e.g. `"Italian"`, `"Japanese"`)
- `price_usd`: float
- `ingredients`: list of strings (at least 4)
- `allergens`: list of strings (possibly empty)
- `is_vegetarian`: boolean
- `preparation_time_minutes`: integer

Your script must:
1. Build a clear structured prompt requesting this schema.
2. Call the LLM (Ollama or OpenAI via the Day 3 client or raw openai SDK).
3. Extract JSON from the raw response using `safe_parse()` (handle prose wrappers and markdown fences).
4. Validate the schema — every key present, correct types.
5. Add business-rule assertions:
   - `price_usd` must be between 1 and 200
   - `ingredients` must have at least 4 items
   - `preparation_time_minutes` must be a positive integer
6. Print the full result: raw response → parsed dict → validation outcome (PASS or FAIL with reasons).
7. Save the parsed JSON to `exercises/data_structures_menu_item.json`.

---

## Part B — Golden Dataset Builder (10 min)

Write a function `build_golden_dataset(items: list[dict]) -> list[dict]` that takes a list of menu item dicts (from the LLM) and converts each into a golden test case in the format used in Day 6:

```python
{
    "id": "menu-{item['name'].lower().replace(' ', '-')}",
    "prompt": f"Describe the menu item called {item['name']}. Return JSON.",
    "must_include": [item["name"], item["cuisine"]],
    "must_not_include": [],
    "min_length": 50,
    "max_length": 500,
    "expects_refusal": False,
}
```

Save the resulting list to `exercises/data_structures_golden.json`.

---

## Part C — Dict Comprehension Challenge (5 min)

Given this list of test results:
```python
results = [
    {"id": "q1", "tag": "factual",  "passed": True,  "score": 0.92},
    {"id": "q2", "tag": "creative", "passed": False,  "score": 0.45},
    {"id": "q3", "tag": "factual",  "passed": True,  "score": 0.88},
    {"id": "q4", "tag": "safety",   "passed": True,  "score": 0.99},
    {"id": "q5", "tag": "creative", "passed": True,  "score": 0.71},
    {"id": "q6", "tag": "factual",  "passed": False,  "score": 0.38},
]
```

Using only comprehensions and built-ins, produce:
1. A dict `{tag: [scores]}` grouping scores by tag.
2. A dict `{tag: avg_score}` with average score per tag (round to 2 dp).
3. A list of IDs for tests that failed.
4. A sorted list of all unique tags, alphabetically.

---

## Self-Check

- [ ] `safe_parse()` handles a response with markdown fences correctly
- [ ] Validation catches a wrong type (e.g., `price_usd` as string)
- [ ] `build_golden_dataset` produces valid Day-6-format test cases
- [ ] `data_structures_menu_item.json` and `data_structures_golden.json` both exist and are valid JSON
- [ ] All Part C comprehensions work without error

## Original Goal (preserved)
Call an LLM, parse its JSON response, and validate it.

## Tasks

1. **Copy and modify** `examples/02_json_parsing.ipynb` into `exercises/data_structures_my_parser.py`.
2. **Change the prompt** to ask for a **restaurant menu item**. It should return JSON with keys:
   - `name` (string)
   - `price_usd` (number)
   - `ingredients` (list of at least 4 strings)
   - `is_vegetarian` (bool)
   - `spice_level` (integer 0–5)
3. **Update `validate_shape`** to check:
   - All keys are present with the right types.
   - `spice_level` is between 0 and 5 inclusive.
   - `ingredients` has at least 4 items.
   - `price_usd` is positive.
4. **Run it 3 times**. Does the model always produce valid JSON? What fails most often?
5. **Write down** in `exercises/data_structures_observations.md`:
   - How many runs out of 3 passed validation?
   - Which field failed most often, and why do you think?

## Self-check

- [ ] Your script runs
- [ ] You understand `dict`, `list`, and nested indexing
- [ ] You know how to extract JSON from a messy response
- [ ] You wrote observations in your own words

## Bonus

Ask the model to return JSON inside a Markdown code fence (```json ... ```). Then update `extract_json` to strip the fences before parsing.
