import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from src.backend.main import app

client = TestClient(app)


def test_websocket_oversized_text_payload():
    with client.websocket_connect("/ws/transcribe") as websocket:
        oversized_payload = "a" * (1024 * 1024 + 10)

        # Exception should be raised when trying to send oversized
        try:
            websocket.send_text(oversized_payload)
            data = websocket.receive()
            # Fastapi TestClient returns a dictionary on normal close instead of raising WebSocketDisconnect
            if isinstance(data, dict) and data.get("type") == "websocket.close":
                assert data.get("code") == 1009
            else:
                assert False, f"Expected connection close, got data: {data}"
        except WebSocketDisconnect as e:
            assert e.code == 1009


def test_websocket_oversized_binary_payload():
    with client.websocket_connect("/ws/transcribe") as websocket:
        # Create a payload > 1MB
        oversized_payload = b"a" * (1024 * 1024 + 10)

        try:
            websocket.send_bytes(oversized_payload)
            data = websocket.receive()
            if isinstance(data, dict) and data.get("type") == "websocket.close":
                assert data.get("code") == 1009
            else:
                assert False, f"Expected connection close, got data: {data}"
        except WebSocketDisconnect as e:
            assert e.code == 1009


def test_websocket_valid_payload():
    with client.websocket_connect("/ws/transcribe") as websocket:
        # Payload < 1MB
        valid_payload = b"a" * (1024)
        websocket.send_bytes(valid_payload)

        # Should not close connection immediately
        # Valid text payload
        websocket.send_json({"action": "clear"})
