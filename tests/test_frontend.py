from playwright.sync_api import Page, expect
import threading
import uvicorn
import pytest
from backend.main import app
import time
import socket

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

def wait_for_port(port: int, host: str = '127.0.0.1', timeout: float = 5.0):
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return
        except OSError:
            time.sleep(0.1)
            if time.time() - start_time >= timeout:
                raise TimeoutError(f"Server on {host}:{port} did not start within {timeout}s.")

@pytest.fixture(scope="module", autouse=True)
def setup_server():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    wait_for_port(8000)
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
    time.sleep(1)

    # Expect text to change to include IPA
    english_val = page.locator("#input-english").input_value()
    assert "h" in english_val

    shavian_text = page.locator("#output-shavian").inner_text()
    assert "𐑣" in shavian_text  # Check for at least one Shavian char
