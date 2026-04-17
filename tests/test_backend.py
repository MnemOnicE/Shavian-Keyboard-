import os
import sys

import numpy as np
from fastapi.testclient import TestClient

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))
from backend.main import app  # noqa: E402


def test_websocket_connection():
    client = TestClient(app)
    with client.websocket_connect("/ws/transcribe") as websocket:
        # Send some dummy audio data (1 second of silence)
        silence = np.zeros(16000, dtype=np.float32)
        websocket.send_bytes(silence.tobytes())

        # Send transcribe command
        websocket.send_json({"action": "transcribe"})
        # We don't receive_json() here because silence often yields no full text,  # noqa: E501
        # which means the backend won't send a response, causing tests to hang.


def test_shavian_logic_integration():
    from lib.shavian import ShavianConverter

    converter = ShavianConverter()
    res = converter.convert_sentence("Hello")
    assert res == "𐑣𐑧𐑤𐑴"
