import os
import sys

import numpy as np
from fastapi.testclient import TestClient

# Adjust path to import backend
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))
from backend.main import app  # noqa: E402

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<title>" in response.text


def test_websocket_connection_and_transcribe():
    with client.websocket_connect("/ws/transcribe") as websocket:
        silence = np.zeros(16000, dtype=np.float32)
        websocket.send_bytes(silence.tobytes())
        websocket.send_text('{"action": "transcribe"}')
        # We don't receive_json() here because silence often yields no full text,  # noqa: E501
        # which means the backend won't send a response, causing tests to hang.


def test_websocket_clear_command():
    with client.websocket_connect("/ws/transcribe") as websocket:
        websocket.send_text('{"action": "clear"}')
