with open("tests/test_websocket_payload_size.py", "r") as f:
    lines = f.read()

lines = lines.replace('import pytest\n', '')
lines = lines.replace('from starlette.websockets import WebSocketDisconnect\n', '')

with open("tests/test_websocket_payload_size.py", "w") as f:
    f.write(lines)
