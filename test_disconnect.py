from fastapi.testclient import TestClient
from src.backend.main import app

client = TestClient(app)

def test_oversized():
    with client.websocket_connect("/ws/transcribe") as websocket:
        oversized_payload = b"a" * (1024 * 1024 + 10)
        websocket.send_bytes(oversized_payload)

        try:
            print(websocket.receive())
        except Exception as e:
            print("EXCEPTION CAUGHT:", type(e), e)

test_oversized()
