"""Integration tests for job_profile status transition endpoints."""
import asyncio
import uuid

import asyncpg
from fastapi.testclient import TestClient

from app.features.auth.utils import get_current_user
from app.features.job_profile.tests.conftest import _create_job_profile


def test_activate_draft_profile(authenticated_client):
    client, _, _ = authenticated_client
    created = _create_job_profile(client)

    resp = client.post(f"/job-profiles/{created['id']}/status/activate")
    assert resp.status_code == 200
    assert resp.json()["status"] == "active"


def test_archive_active_profile(authenticated_client):
    client, _, _ = authenticated_client
    created = _create_job_profile(client)
    client.post(f"/job-profiles/{created['id']}/status/activate")

    resp = client.post(f"/job-profiles/{created['id']}/status/archive")
    assert resp.status_code == 200
    assert resp.json()["status"] == "archived"


def test_activate_archived_profile(authenticated_client):
    client, _, _ = authenticated_client
    created = _create_job_profile(client)
    client.post(f"/job-profiles/{created['id']}/status/archive")

    resp = client.post(f"/job-profiles/{created['id']}/status/activate")
    assert resp.status_code == 200
    assert resp.json()["status"] == "active"


def test_reactivate_already_active_is_idempotent(authenticated_client):
    client, _, _ = authenticated_client
    created = _create_job_profile(client)
    client.post(f"/job-profiles/{created['id']}/status/activate")

    resp = client.post(f"/job-profiles/{created['id']}/status/activate")
    assert resp.status_code == 200
    assert resp.json()["status"] == "active"


def test_cross_user_status_transition_404(app):
    """User B cannot transition User A's job profile status."""
    from app.features.auth.models import create_user, ensure_auth_schema
    from app.features.auth.utils import hash_password
    from app.features.core.config import settings

    async def _make_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            email = f"jp-status-{uuid.uuid4().hex}@example.com"
            user = await create_user(conn, email=email, password_hash=hash_password("x"))
            return dict(user)
        finally:
            await conn.close()

    user_a = asyncio.run(_make_user())
    user_b = asyncio.run(_make_user())

    async def override_a():
        return user_a

    app.dependency_overrides[get_current_user] = override_a
    with TestClient(app) as client_a:
        created = client_a.post("/job-profiles", json={
            "profile_name": f"Status Cross User {uuid.uuid4().hex[:8]}",
        })
        assert created.status_code == 201
        jp_id = created.json()["id"]

    async def override_b():
        return user_b

    app.dependency_overrides[get_current_user] = override_b
    with TestClient(app) as client_b:
        resp = client_b.post(f"/job-profiles/{jp_id}/status/activate")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Job profile not found"

    app.dependency_overrides.clear()

