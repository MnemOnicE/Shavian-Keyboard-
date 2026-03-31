from fastapi.testclient import TestClient
from src.backend.main import app

client = TestClient(app)

def test_websocket_oversized_text_payload():
    with client.websocket_connect("/ws/transcribe") as websocket:
        oversized_payload = "a" * (1024 * 1024 + 10)
        websocket.send_text(oversized_payload)
        data = websocket.receive()
        assert data.get('type') == 'websocket.close'
        assert data.get('code') == 1009

def test_websocket_oversized_binary_payload():
    with client.websocket_connect("/ws/transcribe") as websocket:
        oversized_payload = b"a" * (1024 * 1024 + 10)
        websocket.send_bytes(oversized_payload)
        data = websocket.receive()
        assert data.get('type') == 'websocket.close'
        assert data.get('code') == 1009

def test_websocket_valid_payload():
    with client.websocket_connect("/ws/transcribe") as websocket:
        valid_payload = b"a" * (1024)
        websocket.send_bytes(valid_payload)
        websocket.send_json({"action": "clear"})
