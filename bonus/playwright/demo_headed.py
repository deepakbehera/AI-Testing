#!/usr/bin/env python3
# demo_headed.py — watch Playwright drive a REAL, visible browser.
#
# The notebook and pytest tests run headless (no window). This one opens a
# visible Chromium and slows each step down so you can actually watch it type,
# press Enter, and tick a checkbox — the best way to *see* what an E2E test does.
#
# Run:
#   python demo_headed.py
#
# Needs: pip install -r requirements.txt  &&  playwright install chromium

from playwright.sync_api import sync_playwright, expect

TODOMVC = "https://demo.playwright.dev/todomvc"


def main() -> None:
    with sync_playwright() as p:
        # headless=False -> visible window;  slow_mo -> pause between actions (ms)
        browser = p.chromium.launch(headless=False, slow_mo=800)
        page = browser.new_page()

        print("Opening TodoMVC...")
        page.goto(TODOMVC)

        box = page.get_by_placeholder("What needs to be done?")
        for task in ["Learn Playwright", "Write an E2E test", "Watch it run"]:
            print(f"  adding: {task}")
            box.fill(task)
            box.press("Enter")

        expect(page.get_by_test_id("todo-title")).to_have_count(3)
        print("asserted: 3 todos on screen")

        print("  completing the first todo...")
        page.locator(".todo-list li").first.get_by_role("checkbox").check()
        expect(page.get_by_test_id("todo-count")).to_contain_text("2")
        print("asserted: '2 items left'")

        page.wait_for_timeout(2500)  # linger so you can see the final state
        browser.close()
    print("done")


if __name__ == "__main__":
    main()
