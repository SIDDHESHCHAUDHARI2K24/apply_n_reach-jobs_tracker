"""Integration tests for experience endpoints."""
import uuid
import pytest


def _create_profile(client):
    resp = client.post("/profile")
    assert resp.status_code == 201
    return resp.json()


def _exp_payload(**overrides):
    base = {
        "role_title": "Software Engineer",
        "company_name": "Acme Corp",
        "start_month_year": "01/2020",
        "end_month_year": "12/2022",
        "context": "Built scalable systems.",
        "work_sample_links": [],
        "bullet_points": ["Improved performance by 50%"],
    }
    base.update(overrides)
    return base


def test_list_experiences_empty(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    resp = client.get("/profile/experience")
    assert resp.status_code == 200
    assert resp.json() == []


def test_add_and_list_experience(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    post_resp = client.post("/profile/experience", json=_exp_payload())
    assert post_resp.status_code == 201
    resp = client.get("/profile/experience")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["role_title"] == "Software Engineer"


def test_get_experience_by_id(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    created = client.post("/profile/experience", json=_exp_payload()).json()
    resp = client.get(f"/profile/experience/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_update_experience(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    created = client.post("/profile/experience", json=_exp_payload()).json()
    updated_payload = _exp_payload(role_title="Senior Engineer")
    resp = client.patch(f"/profile/experience/{created['id']}", json=updated_payload)
    assert resp.status_code == 200
    assert resp.json()["role_title"] == "Senior Engineer"


def test_delete_experience(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    created = client.post("/profile/experience", json=_exp_payload()).json()
    resp = client.delete(f"/profile/experience/{created['id']}")
    assert resp.status_code == 204
    # Verify it's gone
    resp2 = client.get(f"/profile/experience/{created['id']}")
    assert resp2.status_code == 404


def test_end_before_start_returns_422(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    resp = client.post("/profile/experience", json=_exp_payload(
        start_month_year="09/2022",
        end_month_year="06/2018",
    ))
    assert resp.status_code == 422


def test_delete_other_users_experience_returns_404(app):
    """Deleting another user's experience entry returns 404 (not 403)."""
    import asyncio
    import asyncpg
    from app.features.core.config import settings
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import get_current_user, hash_password
    from fastapi.testclient import TestClient

    async def _make_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            u = await create_user(conn, email=f"exp-{uuid.uuid4().hex}@example.com", password_hash=hash_password("x"))
            return dict(u)
        finally:
            await conn.close()

    user_a = asyncio.run(_make_user())
    user_b = asyncio.run(_make_user())

    # User A creates a profile and adds an experience entry
    async def override_a(): return user_a
    app.dependency_overrides[get_current_user] = override_a
    with TestClient(app) as ca:
        ca.post("/profile")
        exp = ca.post("/profile/experience", json=_exp_payload()).json()

    # User B tries to delete User A's experience entry
    async def override_b(): return user_b
    app.dependency_overrides[get_current_user] = override_b
    with TestClient(app) as cb:
        # User B has no profile, so get_profile_or_404 returns 404
        resp = cb.delete(f"/profile/experience/{exp['id']}")
        assert resp.status_code == 404

    app.dependency_overrides.clear()


def test_html_in_bullet_points_stripped(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    payload = _exp_payload(bullet_points=["<b>Important</b> achievement"])
    resp = client.post("/profile/experience", json=payload)
    assert resp.status_code == 201
    assert resp.json()["bullet_points"] == ["Important achievement"]


def test_context_field_accepted(authenticated_client):
    """A long context field (up to 10000 chars) saves correctly."""
    client, _ = authenticated_client
    _create_profile(client)
    long_context = "a" * 10000
    resp = client.post("/profile/experience", json=_exp_payload(context=long_context))
    assert resp.status_code == 201
    assert resp.json()["context"] == long_context


def test_context_too_long_returns_422(authenticated_client):
    """Context over 10000 chars returns 422."""
    client, _ = authenticated_client
    _create_profile(client)
    too_long_context = "a" * 10001
    resp = client.post("/profile/experience", json=_exp_payload(context=too_long_context))
    assert resp.status_code == 422


def test_unauthenticated_returns_401(client):
    resp = client.get("/profile/experience")
    assert resp.status_code == 401
