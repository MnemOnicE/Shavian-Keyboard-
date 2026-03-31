import sys
import os
import pytest
from fastapi.testclient import TestClient
import numpy as np

# Adjust path to import backend
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from backend.main import app

client = TestClient(app)

def test_read_root():
    # Test that the frontend static files are served
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<title>" in response.text # Assuming index.html has a title

def test_websocket_connection_and_transcribe():
    # Test WebSocket connection
    with client.websocket_connect("/ws/transcribe") as websocket:
        # Send a command to transcribe (even if buffer is empty, it should handle it safely)
        # However, the code: if len(audio_buffer) > 0: ...
        # If buffer is empty, it does nothing and sends nothing back.

        # Let's send some silent audio first to simulate functionality
        # 16kHz sample rate, 1 second of silence
        # float32 array
        silence = np.zeros(16000, dtype=np.float32)
        websocket.send_bytes(silence.tobytes())

        # Now trigger transcribe
        websocket.send_text('{"action": "transcribe"}')

        # Expect a response. Whisper with silence might return empty string or hallucinate slightly
        # but it should return a JSON with "text" and "shavian" keys.
        data = websocket.receive_json()
        assert "text" in data
        assert "shavian" in data
        # Silence usually results in empty string or simple artifacts
        print(f"Transcription result: {data}")

def test_websocket_clear_command():
     with client.websocket_connect("/ws/transcribe") as websocket:
        websocket.send_text('{"action": "clear"}')
        # No response expected, just verifying it doesn't crash
