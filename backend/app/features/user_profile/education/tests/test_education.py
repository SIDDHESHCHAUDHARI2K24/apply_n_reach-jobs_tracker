"""Integration tests for education endpoints."""
import uuid
import pytest


def _create_profile(client):
    resp = client.post("/profile")
    assert resp.status_code == 201
    return resp.json()


def _edu_payload(**overrides):
    base = {
        "university_name": "MIT",
        "major": "Computer Science",
        "degree_type": "BSc",
        "start_month_year": "09/2018",
        "end_month_year": "06/2022",
        "bullet_points": ["Graduated with honors"],
        "reference_links": [],
    }
    base.update(overrides)
    return base


def test_list_educations_empty(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    resp = client.get("/profile/education")
    assert resp.status_code == 200
    assert resp.json() == []


def test_add_and_list_education(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    post_resp = client.post("/profile/education", json=_edu_payload())
    assert post_resp.status_code == 201
    resp = client.get("/profile/education")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["university_name"] == "MIT"


def test_get_education_by_id(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    created = client.post("/profile/education", json=_edu_payload()).json()
    resp = client.get(f"/profile/education/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_update_education(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    created = client.post("/profile/education", json=_edu_payload()).json()
    updated_payload = _edu_payload(university_name="Harvard")
    resp = client.patch(f"/profile/education/{created['id']}", json=updated_payload)
    assert resp.status_code == 200
    assert resp.json()["university_name"] == "Harvard"


def test_delete_education(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    created = client.post("/profile/education", json=_edu_payload()).json()
    resp = client.delete(f"/profile/education/{created['id']}")
    assert resp.status_code == 204
    # Verify it's gone
    resp2 = client.get(f"/profile/education/{created['id']}")
    assert resp2.status_code == 404


def test_end_before_start_returns_422(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    resp = client.post("/profile/education", json=_edu_payload(
        start_month_year="09/2022",
        end_month_year="06/2018",
    ))
    assert resp.status_code == 422


def test_delete_other_users_education_returns_404(app):
    """Deleting another user's education entry returns 404 (not 403)."""
    import asyncio, asyncpg
    from app.features.core.config import settings
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import get_current_user, hash_password
    from fastapi.testclient import TestClient

    async def _make_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            u = await create_user(conn, email=f"edu-{uuid.uuid4().hex}@example.com", password_hash=hash_password("x"))
            return dict(u)
        finally:
            await conn.close()

    user_a = asyncio.run(_make_user())
    user_b = asyncio.run(_make_user())

    # User A creates a profile and adds an education entry
    async def override_a(): return user_a
    app.dependency_overrides[get_current_user] = override_a
    with TestClient(app) as ca:
        ca.post("/profile")
        edu = ca.post("/profile/education", json=_edu_payload()).json()

    # User B tries to delete User A's education entry
    async def override_b(): return user_b
    app.dependency_overrides[get_current_user] = override_b
    with TestClient(app) as cb:
        # User B has no profile, so get_profile_or_404 returns 404
        resp = cb.delete(f"/profile/education/{edu['id']}")
        assert resp.status_code == 404

    app.dependency_overrides.clear()


def test_html_in_bullet_points_stripped(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    payload = _edu_payload(bullet_points=["<b>Important</b> achievement"])
    resp = client.post("/profile/education", json=payload)
    assert resp.status_code == 201
    assert resp.json()["bullet_points"] == ["Important achievement"]


def test_unauthenticated_returns_401(client):
    resp = client.get("/profile/education")
    assert resp.status_code == 401


def test_partial_update_single_field(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    edu_resp = client.post("/profile/education", json=_edu_payload())
    edu_id = edu_resp.json()["id"]

    resp = client.patch(f"/profile/education/{edu_id}", json={"major": "Physics"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["major"] == "Physics"
    assert data["university_name"] == "MIT"  # unchanged
    assert data["bullet_points"] == ["Graduated with honors"]  # unchanged


def test_partial_update_empty_body_400(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    edu_resp = client.post("/profile/education", json=_edu_payload())
    edu_id = edu_resp.json()["id"]
    resp = client.patch(f"/profile/education/{edu_id}", json={})
    assert resp.status_code == 400
