"""Integration tests for projects endpoints."""
import uuid
import pytest


def _create_profile(client):
    resp = client.post("/profile")
    assert resp.status_code == 201
    return resp.json()


def _proj_payload(**overrides):
    base = {
        "project_name": "My Project",
        "description": "A cool project.",
        "start_month_year": "01/2021",
        "end_month_year": "06/2023",
        "reference_links": [],
    }
    base.update(overrides)
    return base


def test_list_projects_empty(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    resp = client.get("/profile/projects")
    assert resp.status_code == 200
    assert resp.json() == []


def test_add_and_list_project(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    post_resp = client.post("/profile/projects", json=_proj_payload())
    assert post_resp.status_code == 201
    resp = client.get("/profile/projects")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["project_name"] == "My Project"


def test_get_project_by_id(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    created = client.post("/profile/projects", json=_proj_payload()).json()
    resp = client.get(f"/profile/projects/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_update_project(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    created = client.post("/profile/projects", json=_proj_payload()).json()
    updated_payload = _proj_payload(project_name="Updated Project")
    resp = client.patch(f"/profile/projects/{created['id']}", json=updated_payload)
    assert resp.status_code == 200
    assert resp.json()["project_name"] == "Updated Project"


def test_delete_project(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    created = client.post("/profile/projects", json=_proj_payload()).json()
    resp = client.delete(f"/profile/projects/{created['id']}")
    assert resp.status_code == 204
    # Verify it's gone
    resp2 = client.get(f"/profile/projects/{created['id']}")
    assert resp2.status_code == 404


def test_end_before_start_returns_422(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    resp = client.post("/profile/projects", json=_proj_payload(
        start_month_year="09/2022",
        end_month_year="06/2018",
    ))
    assert resp.status_code == 422


def test_delete_other_users_project_returns_404(app):
    """Deleting another user's project entry returns 404 (not 403)."""
    import asyncio, asyncpg
    from app.features.core.config import settings
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import get_current_user, hash_password
    from fastapi.testclient import TestClient

    async def _make_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            u = await create_user(conn, email=f"proj-{uuid.uuid4().hex}@example.com", password_hash=hash_password("x"))
            return dict(u)
        finally:
            await conn.close()

    user_a = asyncio.run(_make_user())
    user_b = asyncio.run(_make_user())

    # User A creates a profile and adds a project entry
    async def override_a(): return user_a
    app.dependency_overrides[get_current_user] = override_a
    with TestClient(app) as ca:
        ca.post("/profile")
        proj = ca.post("/profile/projects", json=_proj_payload()).json()

    # User B tries to delete User A's project entry
    async def override_b(): return user_b
    app.dependency_overrides[get_current_user] = override_b
    with TestClient(app) as cb:
        # User B has no profile, so get_profile_or_404 returns 404
        resp = cb.delete(f"/profile/projects/{proj['id']}")
        assert resp.status_code == 404

    app.dependency_overrides.clear()


def test_html_in_description_stripped(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    payload = _proj_payload(description="<b>Cool</b> project.")
    resp = client.post("/profile/projects", json=payload)
    assert resp.status_code == 201
    assert resp.json()["description"] == "Cool project."


def test_reference_links_rejected_if_not_list(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    payload = _proj_payload(reference_links="https://example.com")
    resp = client.post("/profile/projects", json=payload)
    assert resp.status_code == 422


def test_unauthenticated_returns_401(client):
    resp = client.get("/profile/projects")
    assert resp.status_code == 401


def test_create_project_with_technologies(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    payload = _proj_payload(technologies=["Python", "React"])
    resp = client.post("/profile/projects", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["technologies"] == ["Python", "React"]
    # Verify round-trip via GET
    get_resp = client.get(f"/profile/projects/{data['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["technologies"] == ["Python", "React"]


def test_update_project_technologies(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    created = client.post("/profile/projects", json=_proj_payload(technologies=["Python"])).json()
    assert created["technologies"] == ["Python"]
    updated_payload = _proj_payload(technologies=["TypeScript", "FastAPI", "PostgreSQL"])
    resp = client.patch(f"/profile/projects/{created['id']}", json=updated_payload)
    assert resp.status_code == 200
    assert resp.json()["technologies"] == ["TypeScript", "FastAPI", "PostgreSQL"]
