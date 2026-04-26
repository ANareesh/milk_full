"""Test utilities and helpers."""
from fastapi.testclient import TestClient
from typing import Dict


def get_auth_headers(token: str) -> Dict[str, str]:
    """Create authorization headers."""
    return {"Authorization": f"Bearer {token}"}


def assert_error_response(response, expected_status: int, expected_detail: str = None):
    """Assert error response."""
    assert response.status_code == expected_status
    if expected_detail:
        assert expected_detail in response.json().get("detail", "")
