from fastapi.testclient import TestClient
from src.backend.main import app

client = TestClient(app)


def test_websocket_oversized_text_payload():
    with client.websocket_connect("/ws/transcribe") as websocket:
        # Send a text payload > 1MB
        oversized_payload = "a" * (1024 * 1024 + 10)

        # Exception should be raised when trying to send oversized
        websocket.send_text(oversized_payload)

        response = websocket.receive()
        assert response.get("type") == "websocket.close"
        assert response.get("code") == 1009


def test_websocket_oversized_binary_payload():
    with client.websocket_connect("/ws/transcribe") as websocket:
        # Send a binary payload > 1MB
        oversized_payload = b"a" * (1024 * 1024 + 10)

        websocket.send_bytes(oversized_payload)

        response = websocket.receive()
        assert response.get("type") == "websocket.close"
        assert response.get("code") == 1009


def test_websocket_valid_payload():
    with client.websocket_connect("/ws/transcribe") as websocket:
        # Send a valid binary payload < 1MB
        valid_payload = b"a" * (1024)
        websocket.send_bytes(valid_payload)
        # Should not close connection immediately
        # Valid text payload
        websocket.send_json({"action": "clear"})
