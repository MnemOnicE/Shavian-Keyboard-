with open('tests/test_frontend.py', 'r') as f:
    content = f.read()

new_setup = """import socket
def wait_for_port(port: int, host: str = '127.0.0.1', timeout: float = 5.0):
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return
        except OSError:
            time.sleep(0.1)
            if time.time() - start_time >= timeout:
                raise TimeoutError(f"Server on {host}:{port} did not start within {timeout}s.")

@pytest.fixture(scope="module", autouse=True)
def setup_server():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    wait_for_port(8000)
    yield
"""

import re
content = re.sub(r'@pytest\.fixture\(scope="module", autouse=True\).*?yield\n', new_setup, content, flags=re.DOTALL)

with open('tests/test_frontend.py', 'w') as f:
    f.write(content)
