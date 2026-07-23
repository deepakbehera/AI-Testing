# test_todomvc.py
# The same TodoMVC flow as the notebook, but as real E2E tests — the way
# Playwright is actually used in a project's test suite / CI.
#
# `pytest-playwright` gives every test a ready-to-use `page` fixture (a fresh
# browser page per test), so tests stay short. This uses the SYNC API, which is
# the norm for pytest (the notebook used async because Jupyter has a running
# event loop).
#
# Run:
#   pytest                         # headless, like CI
#   pytest --headed --slowmo 500   # watch the browser do it
#   pytest -k counter -v           # run one test
#
# Needs: pip install -r requirements.txt  &&  playwright install chromium

from playwright.sync_api import Page, expect

TODOMVC = "https://demo.playwright.dev/todomvc"


def add_todos(page: Page, tasks: list[str]) -> None:
    """Helper: type each task into the box and press Enter."""
    box = page.get_by_placeholder("What needs to be done?")
    for task in tasks:
        box.fill(task)
        box.press("Enter")


def test_can_add_todos(page: Page):
    """Typing todos should add exactly that many rows."""
    page.goto(TODOMVC)
    add_todos(page, ["Write a test", "Run it in CI"])
    # Web-first assertion: auto-retries until the DOM has 2 items (no sleep needed).
    expect(page.get_by_test_id("todo-title")).to_have_count(2)


def test_completing_a_todo_updates_the_counter(page: Page):
    """Ticking one todo's checkbox should drop the 'items left' counter."""
    page.goto(TODOMVC)
    add_todos(page, ["a", "b", "c"])
    # Scope to the first todo's OWN checkbox — .first on all checkboxes would hit
    # TodoMVC's hidden 'toggle-all' and complete everything.
    page.locator(".todo-list li").first.get_by_role("checkbox").check()
    expect(page.get_by_test_id("todo-count")).to_contain_text("2")


def test_clear_completed_removes_done_todos(page: Page):
    """'Clear completed' should remove the finished todo, leaving none."""
    page.goto(TODOMVC)
    add_todos(page, ["temporary task"])
    page.locator(".todo-list li").first.get_by_role("checkbox").check()
    page.get_by_role("button", name="Clear completed").click()
    expect(page.get_by_test_id("todo-title")).to_have_count(0)
