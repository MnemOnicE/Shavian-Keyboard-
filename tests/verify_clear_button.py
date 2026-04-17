import os

from playwright.sync_api import expect, sync_playwright


def verify_clear_button():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the HTML file directly
        file_path = os.path.abspath("src/frontend/index.html")
        page.goto(f"file://{file_path}")

        # Check if the Clear button exists and is visible
        clear_btn = page.get_by_role("button", name="Clear")
        expect(clear_btn).to_be_visible()

        # Take a screenshot
        page.screenshot(path="verification/clear_button.png")

        browser.close()


if __name__ == "__main__":
    verify_clear_button()
