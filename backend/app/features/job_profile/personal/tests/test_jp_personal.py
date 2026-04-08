"""Integration tests for job_profile personal details endpoints."""
import uuid
import asyncio
import asyncpg
import pytest
from fastapi.testclient import TestClient

from app.features.auth.models import ensure_auth_schema, create_user
from app.features.auth.utils import get_current_user, hash_password
from app.features.core.config import settings


def _create_job_profile(client):
    resp = client.post("/job-profiles", json={
        "profile_name": f"Test Resume {uuid.uuid4().hex[:8]}",
        "target_role": "Engineer",
    })
    assert resp.status_code == 201
    return resp.json()


class TestGetPersonalDetails:
    def test_get_404_when_empty(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        resp = client.get(f"/job-profiles/{jp['id']}/personal")
        assert resp.status_code == 404

    def test_unauthenticated_401(self, client):
        resp = client.get("/job-profiles/1/personal")
        assert resp.status_code == 401


class TestPatchPersonalDetails:
    def test_create_via_patch_full_payload(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        resp = client.patch(f"/job-profiles/{jp['id']}/personal", json={
            "full_name": "Alice Smith",
            "email": "alice@example.com",
            "linkedin_url": "https://linkedin.com/in/alice",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["full_name"] == "Alice Smith"
        assert data["email"] == "alice@example.com"
        assert data["job_profile_id"] == jp["id"]
        assert data["source_personal_id"] is None

    def test_patch_missing_required_when_empty_returns_404(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        # Only github_url — not enough to create
        resp = client.patch(f"/job-profiles/{jp['id']}/personal", json={
            "github_url": "https://github.com/alice"
        })
        assert resp.status_code == 404

    def test_partial_update_single_field(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        # Create first
        client.patch(f"/job-profiles/{jp['id']}/personal", json={
            "full_name": "Alice Smith",
            "email": "alice@example.com",
            "linkedin_url": "https://linkedin.com/in/alice",
        })
        # Partial update
        resp = client.patch(f"/job-profiles/{jp['id']}/personal", json={
            "github_url": "https://github.com/alice"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["full_name"] == "Alice Smith"  # unchanged
        assert data["github_url"] == "https://github.com/alice"  # updated

    def test_empty_body_patch_returns_400(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        # Create first
        client.patch(f"/job-profiles/{jp['id']}/personal", json={
            "full_name": "Alice", "email": "alice@example.com",
            "linkedin_url": "https://linkedin.com/in/alice"
        })
        # Empty patch
        resp = client.patch(f"/job-profiles/{jp['id']}/personal", json={})
        assert resp.status_code == 400

    def test_html_stripped_from_full_name(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        resp = client.patch(f"/job-profiles/{jp['id']}/personal", json={
            "full_name": "<script>alert(1)</script>Alice",
            "email": "alice@example.com",
            "linkedin_url": "https://linkedin.com/in/alice",
        })
        assert resp.status_code == 200
        assert "<script>" not in resp.json()["full_name"]

    def test_cross_user_access_404(self, app, authenticated_client):
        client_a, _, _ = authenticated_client
        jp_a = _create_job_profile(client_a)

        # Create user B
        async def _create_user_b():
            conn = await asyncpg.connect(settings.database_url)
            try:
                await ensure_auth_schema(conn)
                email = f"user-b-{uuid.uuid4().hex}@example.com"
                user = await create_user(conn, email=email, password_hash=hash_password("pass"))
                return dict(user)
            finally:
                await conn.close()

        user_b = asyncio.run(_create_user_b())

        async def override_b():
            return user_b

        app.dependency_overrides[get_current_user] = override_b
        try:
            with TestClient(app) as client_b:
                resp = client_b.get(f"/job-profiles/{jp_a['id']}/personal")
                assert resp.status_code == 404
        finally:
            app.dependency_overrides.clear()


class TestImportPersonal:
    def _setup_master_personal(self, client):
        """Populate master personal_details."""
        resp = client.patch("/profile/personal", json={
            "full_name": "Master User",
            "email": "master@example.com",
            "linkedin_url": "https://linkedin.com/in/master",
            "github_url": "https://github.com/master",
        })
        assert resp.status_code == 200
        return resp.json()

    def test_import_success(self, authenticated_client):
        client, _, _ = authenticated_client
        self._setup_master_personal(client)
        jp = _create_job_profile(client)
        resp = client.post(f"/job-profiles/{jp['id']}/personal/import")
        assert resp.status_code == 200
        data = resp.json()
        assert data["full_name"] == "Master User"
        assert data["email"] == "master@example.com"
        assert data["source_personal_id"] is not None
        assert data["job_profile_id"] == jp["id"]

    def test_import_overwrites_existing(self, authenticated_client):
        client, _, _ = authenticated_client
        self._setup_master_personal(client)
        jp = _create_job_profile(client)
        # First import
        client.post(f"/job-profiles/{jp['id']}/personal/import")
        # Update master
        client.patch("/profile/personal", json={"full_name": "Updated Name"})
        # Re-import
        resp = client.post(f"/job-profiles/{jp['id']}/personal/import")
        assert resp.status_code == 200
        assert resp.json()["full_name"] == "Updated Name"

    def test_import_no_master_returns_404(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        # No master personal details created
        resp = client.post(f"/job-profiles/{jp['id']}/personal/import")
        assert resp.status_code == 404
