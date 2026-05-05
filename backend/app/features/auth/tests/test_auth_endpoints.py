"""Integration tests for auth endpoints."""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.app import create_app
from app.features.core.config import settings


@pytest.mark.asyncio
async def test_register_and_login_and_me_flow() -> None:
    """User can register, log in, and access /auth/me with a session cookie."""
    app = create_app()
    client = TestClient(app)
    email = f"test-{uuid.uuid4().hex}@example.com"
    password = "strong-password"

    # Register
    resp = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == email

    # Login
    resp = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200
    assert "session_id" in resp.cookies

    # Use cookie to call /auth/me
    cookies = resp.cookies
    resp = client.get("/auth/me", cookies=cookies)
    assert resp.status_code == 200
    me_data = resp.json()
    assert me_data["email"] == email


@pytest.mark.asyncio
async def test_reset_changes_password() -> None:
    """Password reset should allow logging in with the new password."""
    app = create_app()
    client = TestClient(app)
    email = f"reset-{uuid.uuid4().hex}@example.com"
    old_password = "old-password"
    new_password = "new-password"

    # Register user
    resp = client.post(
        "/auth/register",
        json={"email": email, "password": old_password},
    )
    assert resp.status_code == 200

    # Reset password
    resp = client.post(
        "/auth/reset",
        json={"email": email, "password": new_password},
    )
    assert resp.status_code == 200

    # Login with new password should succeed
    resp = client.post(
        "/auth/login",
        json={"email": email, "password": new_password},
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_preflight_uses_explicit_origin_with_credentials() -> None:
    """CORS preflight should echo explicit origin when credentials are enabled."""
    app = create_app()
    client = TestClient(app)
    origin = settings.allowed_origins[0]

    resp = client.options(
        "/auth/login",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert resp.status_code == 200
    assert resp.headers["access-control-allow-origin"] == origin
    assert resp.headers["access-control-allow-credentials"] == "true"

