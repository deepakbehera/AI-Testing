# Browser Testing with Playwright (Python)

Driving a real browser to test what users actually see — click, type, navigate, assert. [Playwright](https://playwright.dev/python/) is the modern tool for browser automation **and** end-to-end (E2E) testing.

## Setup (isolated venv)

```bash
cd bonus/playwright
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium        # one-time: downloads the browser (~150 MB)
```

## What's here

| File | What it is | Run it |
|---|---|---|
| [`playwright_intro.ipynb`](playwright_intro.ipynb) | Live walkthrough: launch a browser, screenshot, locators, and interact with the official TodoMVC demo (uses the **async** API, which works in Jupyter) | open in Jupyter/VSCode with this `.venv` |
| [`test_todomvc.py`](test_todomvc.py) | The same flow as **`pytest` E2E tests** (the production shape, with the `page` fixture) | `pytest` · `pytest --headed --slowmo 500` |
| [`demo_headed.py`](demo_headed.py) | A **visible** browser you can watch drive the flow, step by step | `python demo_headed.py` |

## Why Playwright is good for *testing*

- **Auto-waiting** — waits for elements to be actionable before clicking/typing. No `sleep()`; kills the #1 cause of flaky UI tests.
- **Locators** — address elements by meaning (`get_by_role`, `get_by_text`, `get_by_test_id`), robust to layout changes.
- **Web-first assertions** — `expect(locator).to_have_text(...)` **auto-retries** until it passes or times out.

Same testing mindset as the rest of the course: assert on real user-facing behaviour, and make the check robust to the system's timing.

> All demos run against public practice sites (`example.com`, `playwright.dev`, `demo.playwright.dev/todomvc`) — nothing to host.
