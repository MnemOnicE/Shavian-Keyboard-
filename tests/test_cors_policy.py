import os
import sys

from fastapi.testclient import TestClient

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))
from backend.main import app  # noqa: E402


def test_cors_options_allowed_methods():
    client = TestClient(app)
    # Origin must be one of the allowed origins for CORS middleware to process it  # noqa: E501
    origin = "http://localhost:8000"
    headers = {
        "Origin": origin,
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "Content-Type",
    }
    response = client.options("/", headers=headers)

    assert response.status_code == 200
    # Access-Control-Allow-Methods should contain GET
    allowed_methods = response.headers.get("Access-Control-Allow-Methods", "")
    assert "GET" in allowed_methods
    # Wildcard was removed, so other methods should not be present
    assert "POST" not in allowed_methods
    assert "DELETE" not in allowed_methods

    # Access-Control-Allow-Headers should contain Content-Type
    allowed_headers = response.headers.get("Access-Control-Allow-Headers", "")
    assert "Content-Type" in allowed_headers


def test_cors_options_disallowed_method():
    client = TestClient(app)
    origin = "http://localhost:8000"
    headers = {
        "Origin": origin,
        "Access-Control-Request-Method": "POST",
    }
    response = client.options("/", headers=headers)

    # If the method is not allowed, the CORS middleware should not return allow headers  # noqa: E501
    assert response.status_code == 400


def test_cors_disallowed_origin():
    client = TestClient(app)
    origin = "http://malicious.com"
    headers = {
        "Origin": origin,
        "Access-Control-Request-Method": "GET",
    }
    response = client.options("/", headers=headers)

    # If origin is not allowed, CORS headers should not be present
    assert "Access-Control-Allow-Origin" not in response.headers
