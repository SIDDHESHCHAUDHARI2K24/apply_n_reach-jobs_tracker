"""Integration tests for skills endpoints."""
import uuid
import pytest


def _create_profile(client):
    resp = client.post("/profile")
    assert resp.status_code == 201
    return resp.json()


def test_list_skills_empty(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    resp = client.get("/profile/skills")
    assert resp.status_code == 200
    assert resp.json() == []


def test_patch_skills_replace(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    payload = {
        "skills": [
            {"kind": "technical", "name": "Python", "sort_order": 0},
            {"kind": "competency", "name": "Leadership", "sort_order": 1},
        ]
    }
    resp = client.patch("/profile/skills", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    names = {s["name"] for s in data}
    assert names == {"Python", "Leadership"}


def test_patch_skills_full_replace(authenticated_client):
    """Second PATCH replaces the entire skill set, not just adds to it."""
    client, _ = authenticated_client
    _create_profile(client)
    client.patch("/profile/skills", json={"skills": [
        {"kind": "technical", "name": "Python", "sort_order": 0},
    ]})
    resp = client.patch("/profile/skills", json={"skills": [
        {"kind": "technical", "name": "Go", "sort_order": 0},
    ]})
    assert resp.status_code == 200
    names = [s["name"] for s in resp.json()]
    assert names == ["Go"]
    assert "Python" not in names


def test_patch_skills_empty_list_returns_422(authenticated_client):
    """PATCH with empty skills list returns 422 — at least one skill required."""
    client, _ = authenticated_client
    _create_profile(client)
    resp = client.patch("/profile/skills", json={"skills": []})
    assert resp.status_code == 422


def test_get_skill_by_id(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    client.patch("/profile/skills", json={"skills": [
        {"kind": "technical", "name": "Python", "sort_order": 0},
    ]})
    skill_id = client.get("/profile/skills").json()[0]["id"]
    resp = client.get(f"/profile/skills/{skill_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Python"


def test_get_skill_wrong_id_returns_404(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    resp = client.get("/profile/skills/99999999")
    assert resp.status_code == 404


def test_get_skill_other_users_returns_404(app):
    """GET /profile/skills/{id} for another user's skill returns 404."""
    import asyncio, asyncpg
    from app.features.core.config import settings
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import get_current_user, hash_password
    from fastapi.testclient import TestClient

    async def _make_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            u = await create_user(conn, email=f"skill-{uuid.uuid4().hex}@example.com", password_hash=hash_password("x"))
            return dict(u)
        finally:
            await conn.close()

    user_a = asyncio.run(_make_user())
    user_b = asyncio.run(_make_user())

    async def override_a(): return user_a
    app.dependency_overrides[get_current_user] = override_a
    with TestClient(app) as ca:
        ca.post("/profile")
        ca.patch("/profile/skills", json={"skills": [{"kind": "technical", "name": "Python", "sort_order": 0}]})
        skill_id = ca.get("/profile/skills").json()[0]["id"]

    async def override_b(): return user_b
    app.dependency_overrides[get_current_user] = override_b
    with TestClient(app) as cb:
        cb.post("/profile")
        resp = cb.get(f"/profile/skills/{skill_id}")
        assert resp.status_code == 404

    app.dependency_overrides.clear()


def test_html_in_skill_name_stripped(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    resp = client.patch("/profile/skills", json={"skills": [
        {"kind": "technical", "name": "<b>Python</b>", "sort_order": 0},
    ]})
    assert resp.status_code == 200
    assert resp.json()[0]["name"] == "Python"


def test_skill_name_too_long_returns_422(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    resp = client.patch("/profile/skills", json={"skills": [
        {"kind": "technical", "name": "x" * 101, "sort_order": 0},
    ]})
    assert resp.status_code == 422


def test_invalid_kind_returns_422(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    resp = client.patch("/profile/skills", json={"skills": [
        {"kind": "invalid_kind", "name": "Python", "sort_order": 0},
    ]})
    assert resp.status_code == 422


def test_unauthenticated_returns_401(client):
    resp = client.get("/profile/skills")
    assert resp.status_code == 401
