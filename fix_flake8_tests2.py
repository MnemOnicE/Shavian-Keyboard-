with open("tests/test_websocket_payload_size.py", "r") as f:
    lines = f.read()

lines = lines.replace(
    '        with pytest.raises(WebSocketDisconnect) as exc_info:\n            # Server should close connection with code 1009\n            websocket.receive()\n\n        assert exc_info.value.code == 1009',
    '        response = websocket.receive()\n        assert response.get("type") == "websocket.close"\n        assert response.get("code") == 1009'
)

with open("tests/test_websocket_payload_size.py", "w") as f:
    f.write(lines)
