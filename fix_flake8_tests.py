with open("tests/test_websocket_payload_size.py", "r") as f:
    lines = f.read()

lines = lines.replace(
    '            data = websocket.receive()\n            \n        assert exc_info.value.code == 1009',
    '            websocket.receive()\n\n        assert exc_info.value.code == 1009'
)

with open("tests/test_websocket_payload_size.py", "w") as f:
    f.write(lines)
