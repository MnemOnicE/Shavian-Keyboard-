from playwright.sync_api import Page, expect
import threading
import uvicorn
import pytest
from src.backend.main import app
import time

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

@pytest.fixture(scope="module", autouse=True)
def setup_server():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(2)  # Wait for server to start
    yield

def test_frontend_layout(page: Page):
    page.goto("http://127.0.0.1:8000/")

    # Check basic UI elements
    expect(page.locator("h1")).to_have_text("AutoShavian")
    expect(page.locator("#btn-record")).to_be_visible()
    expect(page.locator("#mic-mode-toggle")).to_be_attached()
    expect(page.locator("#input-english")).to_be_visible()
    expect(page.locator("#btn-translate")).to_be_visible()
    expect(page.locator("#output-shavian")).to_be_visible()

    # Test typing in English text box
    page.fill("#input-english", "Hello world")

    # Test translation API via clicking translate
    page.click("#btn-translate")

    # Wait for websocket roundtrip
    # Wait for the websocket roundtrip and DOM update using Playwright's auto-waiting.
    expect(page.locator("#input-english")).to_contain_text("[/həˈloʊ/]")

    # Check for the correct Shavian translation of "Hello world"
    expect(page.locator("#output-shavian")).to_have_text("𐑣𐑧𐑤𐑴 𐑢𐑻𐑤𐑛")
