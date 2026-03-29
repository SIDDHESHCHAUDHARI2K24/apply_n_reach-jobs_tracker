"""Canary tests that validate the test fixture infrastructure is working correctly.

Run these before writing any feature tests to confirm:
1. authenticated_client fixture injects a valid user (bypasses real auth)
2. Unauthenticated requests to protected endpoints return 401
"""
import pytest


def test_unauthenticated_request_returns_401(client):
    """A request to a protected endpoint without auth must return 401."""
    # GET /auth/me is a stable protected endpoint that always exists
    resp = client.get("/auth/me")
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


def test_authenticated_client_bypasses_auth(authenticated_client):
    """authenticated_client fixture must inject a user without a real session cookie.

    POST /profile returns 201 (profile created) or 409 (already exists) but NOT 401,
    confirming the auth override is working.
    """
    client, user_data = authenticated_client
    assert user_data["id"] is not None, "Test user must have an id"

    resp = client.post("/profile")
    assert resp.status_code in (201, 409, 404), (
        f"Expected 201/409/404 (not 401), got {resp.status_code}: {resp.text}"
    )
