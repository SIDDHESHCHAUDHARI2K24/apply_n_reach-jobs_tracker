"""Tests for job opening CRUD operations."""
import uuid


def test_create_opening_201(auth_client):
    client, user_data = auth_client
    company = f"Test Co {uuid.uuid4().hex[:8]}"
    resp = client.post(
        "/job-openings",
        json={"company_name": company, "role_name": "Backend Engineer", "notes": "Nice job"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["company_name"] == company
    assert body["role_name"] == "Backend Engineer"
    assert body["notes"] == "Nice job"
    assert body["current_status"] == "Interested"
    assert body["user_id"] == user_data["id"]
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_create_opening_with_initial_status(auth_client):
    client, _ = auth_client
    resp = client.post(
        "/job-openings",
        json={
            "company_name": f"Corp {uuid.uuid4().hex[:8]}",
            "role_name": "Engineer",
            "initial_status": "Applied",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["current_status"] == "Applied"


def test_get_opening_200(auth_client, sample_opening):
    client, _ = auth_client
    opening_id = sample_opening["id"]
    resp = client.get(f"/job-openings/{opening_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == opening_id
    assert body["company_name"] == sample_opening["company_name"]


def test_get_opening_not_found_404(auth_client):
    client, _ = auth_client
    resp = client.get("/job-openings/999999999")
    assert resp.status_code == 404


def test_patch_opening_200(auth_client, sample_opening):
    client, _ = auth_client
    opening_id = sample_opening["id"]
    resp = client.patch(
        f"/job-openings/{opening_id}",
        json={"role_name": "Senior Engineer"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["role_name"] == "Senior Engineer"
    # company_name should remain unchanged
    assert body["company_name"] == sample_opening["company_name"]
    assert body["notes"] == sample_opening["notes"]


def test_patch_opening_no_fields_400(auth_client, sample_opening):
    client, _ = auth_client
    opening_id = sample_opening["id"]
    resp = client.patch(f"/job-openings/{opening_id}", json={})
    assert resp.status_code == 400


def test_delete_opening_204(auth_client, sample_opening):
    client, _ = auth_client
    opening_id = sample_opening["id"]
    resp = client.delete(f"/job-openings/{opening_id}?confirm=true")
    assert resp.status_code == 204


def test_get_deleted_opening_404(auth_client, sample_opening):
    client, _ = auth_client
    opening_id = sample_opening["id"]
    client.delete(f"/job-openings/{opening_id}?confirm=true")
    resp = client.get(f"/job-openings/{opening_id}")
    assert resp.status_code == 404


def test_cross_user_isolation(app, auth_client, sample_opening):
    """Another user cannot see the first user's opening."""
    import asyncio
    import asyncpg
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import get_current_user, hash_password
    from app.features.core.config import settings
    from fastapi.testclient import TestClient

    opening_id = sample_opening["id"]

    async def _create_second_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            email = f"test-other-{uuid.uuid4().hex}@example.com"
            user = await create_user(
                conn, email=email, password_hash=hash_password("testpass2")
            )
            return dict(user)
        finally:
            await conn.close()

    other_user = asyncio.run(_create_second_user())

    async def override_other_user():
        return other_user

    app.dependency_overrides[get_current_user] = override_other_user

    with TestClient(app) as other_client:
        resp = other_client.get(f"/job-openings/{opening_id}")
        assert resp.status_code == 404

    app.dependency_overrides.clear()
