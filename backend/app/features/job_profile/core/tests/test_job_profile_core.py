"""Integration tests for job profile core CRUD endpoints."""
import uuid
import asyncio
import asyncpg
import pytest
from fastapi.testclient import TestClient

from app.features.job_profile.tests.conftest import _create_job_profile


def test_create_job_profile(authenticated_client):
    client, user_data, _ = authenticated_client
    resp = client.post("/job-profiles", json={
        "profile_name": f"My Resume {uuid.uuid4().hex[:8]}",
        "target_role": "SWE",
        "target_company": "Google",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["target_role"] == "SWE"
    assert data["status"] == "draft"
    assert data["user_id"] == user_data["id"]


def test_create_auto_imports_personal_snapshot_when_master_exists(authenticated_client):
    client, _, _ = authenticated_client
    personal_payload = {
        "full_name": "Snapshot User",
        "email": "snapshot@example.com",
        "linkedin_url": "https://linkedin.com/in/snapshot",
        "github_url": "https://github.com/snapshot",
    }
    setup_resp = client.patch("/profile/personal", json=personal_payload)
    assert setup_resp.status_code == 200

    create_resp = client.post("/job-profiles", json={
        "profile_name": f"Snapshot Resume {uuid.uuid4().hex[:8]}",
        "target_role": "SWE",
    })
    assert create_resp.status_code == 201
    jp_id = create_resp.json()["id"]

    personal_resp = client.get(f"/job-profiles/{jp_id}/personal")
    assert personal_resp.status_code == 200
    personal_data = personal_resp.json()
    assert personal_data["full_name"] == "Snapshot User"
    assert personal_data["email"] == "snapshot@example.com"
    assert personal_data["linkedin_url"] == "https://linkedin.com/in/snapshot"
    assert personal_data["source_personal_id"] is not None


def test_create_succeeds_without_master_personal_snapshot(authenticated_client):
    client, _, _ = authenticated_client
    create_resp = client.post("/job-profiles", json={
        "profile_name": f"No Personal Resume {uuid.uuid4().hex[:8]}",
    })
    assert create_resp.status_code == 201
    jp_id = create_resp.json()["id"]

    personal_resp = client.get(f"/job-profiles/{jp_id}/personal")
    assert personal_resp.status_code == 404
    assert personal_resp.json()["detail"] == "Personal details not found"


def test_create_duplicate_name_409(authenticated_client):
    client, _, _ = authenticated_client
    name = f"Duplicate Resume {uuid.uuid4().hex[:8]}"
    client.post("/job-profiles", json={"profile_name": name})
    resp = client.post("/job-profiles", json={"profile_name": name})
    assert resp.status_code == 409


def test_list_empty(authenticated_client):
    client, _, _ = authenticated_client
    resp = client.get("/job-profiles")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_pagination(authenticated_client):
    client, _, _ = authenticated_client
    # Create 3 job profiles
    for i in range(3):
        _create_job_profile(client)

    # Fetch with limit=2
    resp = client.get("/job-profiles?limit=2&offset=0")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["total"] >= 3
    assert data["limit"] == 2
    assert data["offset"] == 0


def test_list_filter_status(authenticated_client):
    client, _, _ = authenticated_client
    # Create draft and active profiles
    draft = _create_job_profile(client)
    active_profile = _create_job_profile(client)
    # Update one to active
    client.patch(f"/job-profiles/{active_profile['id']}", json={"status": "active"})

    resp = client.get("/job-profiles?status=active")
    assert resp.status_code == 200
    data = resp.json()
    assert all(item["status"] == "active" for item in data["items"])
    assert data["total"] >= 1


def test_get_by_id(authenticated_client):
    client, _, _ = authenticated_client
    created = _create_job_profile(client)
    resp = client.get(f"/job-profiles/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]
    assert resp.json()["profile_name"] == created["profile_name"]


def test_get_nonexistent_404(authenticated_client):
    client, _, _ = authenticated_client
    resp = client.get("/job-profiles/99999999")
    assert resp.status_code == 404


def test_partial_update(authenticated_client):
    client, _, _ = authenticated_client
    created = _create_job_profile(client)
    resp = client.patch(f"/job-profiles/{created['id']}", json={
        "target_role": "Staff Engineer"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["target_role"] == "Staff Engineer"
    assert data["target_company"] == created["target_company"]  # unchanged


def test_update_status(authenticated_client):
    client, _, _ = authenticated_client
    created = _create_job_profile(client)
    resp = client.patch(f"/job-profiles/{created['id']}", json={"status": "active"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "active"


def test_update_empty_body_400(authenticated_client):
    client, _, _ = authenticated_client
    created = _create_job_profile(client)
    resp = client.patch(f"/job-profiles/{created['id']}", json={})
    assert resp.status_code == 400


def test_delete(authenticated_client):
    client, _, _ = authenticated_client
    created = _create_job_profile(client)
    resp = client.delete(f"/job-profiles/{created['id']}")
    assert resp.status_code == 204

    # Verify it's gone
    resp2 = client.get(f"/job-profiles/{created['id']}")
    assert resp2.status_code == 404


def test_unauthenticated_401(client):
    resp = client.get("/job-profiles")
    assert resp.status_code == 401

    resp2 = client.post("/job-profiles", json={"profile_name": "test"})
    assert resp2.status_code == 401


def test_cross_user_404(app):
    """User B cannot access or modify User A's job profile."""
    from app.features.core.config import settings

    async def _make_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            from app.features.auth.models import ensure_auth_schema, create_user
            from app.features.auth.utils import hash_password
            await ensure_auth_schema(conn)
            email = f"jp-cross-{uuid.uuid4().hex}@example.com"
            u = await create_user(conn, email=email, password_hash=hash_password("x"))
            return dict(u)
        finally:
            await conn.close()

    user_a = asyncio.run(_make_user())
    user_b = asyncio.run(_make_user())

    from app.features.auth.utils import get_current_user

    # User A creates a job profile
    async def override_a():
        return user_a
    app.dependency_overrides[get_current_user] = override_a
    with TestClient(app) as ca:
        resp = ca.post("/job-profiles", json={
            "profile_name": f"User A Profile {uuid.uuid4().hex[:8]}"
        })
        assert resp.status_code == 201
        jp_id = resp.json()["id"]

    # User B tries to access User A's job profile
    async def override_b():
        return user_b
    app.dependency_overrides[get_current_user] = override_b
    with TestClient(app) as cb:
        resp = cb.get(f"/job-profiles/{jp_id}")
        assert resp.status_code == 404

        resp2 = cb.delete(f"/job-profiles/{jp_id}")
        assert resp2.status_code == 404

    app.dependency_overrides.clear()


def test_cap_at_50(authenticated_client):
    """Creating more than 50 job profiles returns 409."""
    client, _, _ = authenticated_client
    # Create 50 profiles
    for i in range(50):
        resp = client.post("/job-profiles", json={
            "profile_name": f"Profile Cap Test {i} {uuid.uuid4().hex[:8]}"
        })
        assert resp.status_code == 201, f"Failed at profile {i}: {resp.status_code}"

    # 51st should fail
    resp = client.post("/job-profiles", json={
        "profile_name": f"Profile 51 {uuid.uuid4().hex[:8]}"
    })
    assert resp.status_code == 409
