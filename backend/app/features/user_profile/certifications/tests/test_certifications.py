"""Integration tests for certifications endpoints."""
import uuid
import pytest


def _create_profile(client):
    resp = client.post("/profile")
    assert resp.status_code == 201
    return resp.json()


def _cert_payload(**overrides):
    base = {
        "certification_name": "AWS Solutions Architect",
        "verification_link": "https://aws.amazon.com/certification/verify",
    }
    base.update(overrides)
    return base


def test_list_certifications_empty(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    resp = client.get("/profile/certifications")
    assert resp.status_code == 200
    assert resp.json() == []


def test_add_and_list_certification(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    post_resp = client.post("/profile/certifications", json=_cert_payload())
    assert post_resp.status_code == 201
    resp = client.get("/profile/certifications")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["certification_name"] == "AWS Solutions Architect"


def test_get_certification_by_id(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    created = client.post("/profile/certifications", json=_cert_payload()).json()
    resp = client.get(f"/profile/certifications/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_update_certification(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    created = client.post("/profile/certifications", json=_cert_payload()).json()
    updated_payload = _cert_payload(certification_name="Google Cloud Professional")
    resp = client.patch(f"/profile/certifications/{created['id']}", json=updated_payload)
    assert resp.status_code == 200
    assert resp.json()["certification_name"] == "Google Cloud Professional"


def test_delete_certification(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    created = client.post("/profile/certifications", json=_cert_payload()).json()
    resp = client.delete(f"/profile/certifications/{created['id']}")
    assert resp.status_code == 204
    # Verify it's gone
    resp2 = client.get(f"/profile/certifications/{created['id']}")
    assert resp2.status_code == 404


def test_delete_other_users_certification_returns_404(app):
    """Deleting another user's certification entry returns 404 (not 403)."""
    import asyncio, asyncpg
    from app.features.core.config import settings
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import get_current_user, hash_password
    from fastapi.testclient import TestClient

    async def _make_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            u = await create_user(conn, email=f"cert-{uuid.uuid4().hex}@example.com", password_hash=hash_password("x"))
            return dict(u)
        finally:
            await conn.close()

    user_a = asyncio.run(_make_user())
    user_b = asyncio.run(_make_user())

    # User A creates a profile and adds a certification entry
    async def override_a(): return user_a
    app.dependency_overrides[get_current_user] = override_a
    with TestClient(app) as ca:
        ca.post("/profile")
        cert = ca.post("/profile/certifications", json=_cert_payload()).json()

    # User B tries to delete User A's certification entry
    async def override_b(): return user_b
    app.dependency_overrides[get_current_user] = override_b
    with TestClient(app) as cb:
        # User B has no profile, so get_profile_or_404 returns 404
        resp = cb.delete(f"/profile/certifications/{cert['id']}")
        assert resp.status_code == 404

    app.dependency_overrides.clear()


def test_html_in_certification_name_stripped(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    payload = _cert_payload(certification_name="<b>AWS</b> Solutions Architect")
    resp = client.post("/profile/certifications", json=payload)
    assert resp.status_code == 201
    assert resp.json()["certification_name"] == "AWS Solutions Architect"


def test_unauthenticated_returns_401(client):
    resp = client.get("/profile/certifications")
    assert resp.status_code == 401
