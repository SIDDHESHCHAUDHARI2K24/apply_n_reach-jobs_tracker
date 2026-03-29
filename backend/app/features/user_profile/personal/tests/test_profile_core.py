"""Integration tests for core profile and personal details endpoints."""
import uuid
import pytest
from fastapi.testclient import TestClient


# ─── POST /profile ──────────────────────────────────────────────────────────

def test_create_profile_success(authenticated_client):
    """Authenticated user can create a profile (201)."""
    client, _ = authenticated_client
    resp = client.post("/profile")
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data


def test_create_profile_duplicate(authenticated_client):
    """Second call to POST /profile returns 409."""
    client, _ = authenticated_client
    resp1 = client.post("/profile")
    assert resp1.status_code == 201
    resp2 = client.post("/profile")
    assert resp2.status_code == 409


def test_create_profile_unauthenticated(client):
    """POST /profile without auth returns 401."""
    resp = client.post("/profile")
    assert resp.status_code == 401


# ─── GET /profile/personal ──────────────────────────────────────────────────

def test_get_personal_no_profile(authenticated_client):
    """GET /profile/personal returns 404 when no profile exists yet."""
    client, _ = authenticated_client
    # Do NOT create profile — dependency will 404
    resp = client.get("/profile/personal")
    assert resp.status_code == 404


def test_get_personal_not_yet_upserted(authenticated_client):
    """GET /profile/personal returns 404 when profile exists but personal details not set."""
    client, _ = authenticated_client
    client.post("/profile")  # create profile
    resp = client.get("/profile/personal")
    assert resp.status_code == 404


def test_get_personal_success(authenticated_client):
    """GET /profile/personal returns 200 with data after a PATCH."""
    client, _ = authenticated_client
    client.post("/profile")
    client.patch("/profile/personal", json={
        "full_name": "Jane Doe",
        "email": f"jane-{uuid.uuid4().hex}@example.com",
        "linkedin_url": "https://linkedin.com/in/jane",
    })
    resp = client.get("/profile/personal")
    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "Jane Doe"


def test_get_personal_unauthenticated(client):
    """GET /profile/personal without auth returns 401."""
    resp = client.get("/profile/personal")
    assert resp.status_code == 401


# ─── PATCH /profile/personal ────────────────────────────────────────────────

def test_patch_personal_create(authenticated_client):
    """First PATCH creates personal details."""
    client, _ = authenticated_client
    client.post("/profile")
    email = f"patch-{uuid.uuid4().hex}@example.com"
    resp = client.patch("/profile/personal", json={
        "full_name": "John Smith",
        "email": email,
        "linkedin_url": "https://linkedin.com/in/john",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "John Smith"
    assert data["email"] == email


def test_patch_personal_update(authenticated_client):
    """Second PATCH updates existing personal details."""
    client, _ = authenticated_client
    client.post("/profile")
    email = f"upd-{uuid.uuid4().hex}@example.com"
    client.patch("/profile/personal", json={
        "full_name": "Original Name",
        "email": email,
        "linkedin_url": "https://linkedin.com/in/original",
    })
    resp = client.patch("/profile/personal", json={
        "full_name": "Updated Name",
        "email": email,
        "linkedin_url": "https://linkedin.com/in/updated",
    })
    assert resp.status_code == 200
    assert resp.json()["full_name"] == "Updated Name"


def test_patch_personal_invalid_email(authenticated_client):
    """PATCH /profile/personal with invalid email returns 422."""
    client, _ = authenticated_client
    client.post("/profile")
    resp = client.patch("/profile/personal", json={
        "full_name": "Test User",
        "email": "not-valid-email",
        "linkedin_url": "https://linkedin.com/in/test",
    })
    assert resp.status_code == 422


def test_patch_personal_html_stripped(authenticated_client):
    """HTML in full_name is stripped before storage."""
    client, _ = authenticated_client
    client.post("/profile")
    email = f"html-{uuid.uuid4().hex}@example.com"
    resp = client.patch("/profile/personal", json={
        "full_name": "<script>alert('xss')</script>Real Name",
        "email": email,
        "linkedin_url": "https://linkedin.com/in/real",
    })
    assert resp.status_code == 200
    assert resp.json()["full_name"] == "Real Name"


def test_patch_personal_unauthenticated(client):
    """PATCH /profile/personal without auth returns 401."""
    resp = client.patch("/profile/personal", json={
        "full_name": "Test",
        "email": "test@example.com",
        "linkedin_url": "https://linkedin.com/in/test",
    })
    assert resp.status_code == 401


# ─── Ownership isolation ─────────────────────────────────────────────────────

def test_ownership_isolation(app):
    """User B cannot access User A's personal details.

    Creates two separate authenticated clients with different users.
    User A creates a profile and patches personal details.
    User B's request for /profile/personal returns 404 (not User A's data).
    """
    import asyncio, asyncpg
    from app.features.core.config import settings
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import get_current_user, hash_password

    async def _make_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            email = f"owner-{uuid.uuid4().hex}@example.com"
            u = await create_user(conn, email=email, password_hash=hash_password("x"))
            return dict(u)
        finally:
            await conn.close()

    user_a = asyncio.run(_make_user())
    user_b = asyncio.run(_make_user())

    # Client for User A
    async def override_a():
        return user_a
    app.dependency_overrides[get_current_user] = override_a
    with TestClient(app) as client_a:
        client_a.post("/profile")
        client_a.patch("/profile/personal", json={
            "full_name": "User A",
            "email": user_a["email"],
            "linkedin_url": "https://linkedin.com/in/a",
        })

    # Client for User B — must NOT see User A's data
    async def override_b():
        return user_b
    app.dependency_overrides[get_current_user] = override_b
    with TestClient(app) as client_b:
        resp = client_b.get("/profile/personal")
        # User B has no profile yet → 404 from get_profile_or_404
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    app.dependency_overrides.clear()
