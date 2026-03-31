import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from backend.main import app

def test_websocket_connection():
    client = TestClient(app)
    with client.websocket_connect("/ws/transcribe") as websocket:
        # Send some dummy audio data (1 second of silence)
        # 16000 samples * 4 bytes (float32)
        silence = np.zeros(16000, dtype=np.float32)
        websocket.send_bytes(silence.tobytes())

        # Send transcribe command
        websocket.send_json({"action": "transcribe"})

        # Receive response
        data = websocket.receive_json()
        assert "text" in data
        assert "shavian" in data
        # Silence usually results in empty text or hallucinations.
        # faster-whisper might return nothing or "..."
        print(f"Response: {data}")

def test_shavian_logic_integration():
    # Test the converter specifically
    from lib.shavian import ShavianConverter
    converter = ShavianConverter()
    res = converter.convert_sentence("Hello")
    assert res == "𐑣𐑧𐑤𐑴" # Based on previous run
