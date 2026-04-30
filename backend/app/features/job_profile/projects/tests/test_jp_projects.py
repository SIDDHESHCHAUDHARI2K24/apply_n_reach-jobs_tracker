"""Integration tests for job_profile projects endpoints."""
import uuid
import asyncio
import asyncpg
import pytest

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


def _add_project(client, job_profile_id, **overrides):
    payload = {
        "project_name": "My App",
        "description": "A cool application",
        "start_month_year": "01/2023",
        **overrides,
    }
    resp = client.post(f"/job-profiles/{job_profile_id}/projects", json=payload)
    assert resp.status_code == 201
    return resp.json()


class TestCRUD:
    def test_list_empty(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        resp = client.get(f"/job-profiles/{jp['id']}/projects")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_add_and_list(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        _add_project(client, jp["id"])
        _add_project(client, jp["id"], project_name="Another App")
        resp = client.get(f"/job-profiles/{jp['id']}/projects")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_by_id(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        proj = _add_project(client, jp["id"])
        resp = client.get(f"/job-profiles/{jp['id']}/projects/{proj['id']}")
        assert resp.status_code == 200
        assert resp.json()["project_name"] == "My App"

    def test_get_nonexistent_404(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        resp = client.get(f"/job-profiles/{jp['id']}/projects/99999")
        assert resp.status_code == 404

    def test_delete(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        proj = _add_project(client, jp["id"])
        resp = client.delete(f"/job-profiles/{jp['id']}/projects/{proj['id']}")
        assert resp.status_code == 204
        assert client.get(f"/job-profiles/{jp['id']}/projects/{proj['id']}").status_code == 404

    def test_partial_update_single_field(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        proj = _add_project(client, jp["id"])
        resp = client.patch(f"/job-profiles/{jp['id']}/projects/{proj['id']}", json={
            "description": "Updated description"
        })
        assert resp.status_code == 200
        assert resp.json()["description"] == "Updated description"
        assert resp.json()["project_name"] == "My App"  # unchanged

    def test_partial_update_empty_body_400(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        proj = _add_project(client, jp["id"])
        resp = client.patch(f"/job-profiles/{jp['id']}/projects/{proj['id']}", json={})
        assert resp.status_code == 400

    def test_source_project_id_null(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        proj = _add_project(client, jp["id"])
        assert proj["source_project_id"] is None

    def test_reference_links_roundtrip(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        proj = _add_project(client, jp["id"],
                            reference_links=["https://github.com/test/repo"])
        assert proj["reference_links"] == ["https://github.com/test/repo"]

    def test_unauthenticated_401(self, client):
        resp = client.get("/job-profiles/1/projects")
        assert resp.status_code == 401


class TestValidation:
    def test_end_before_start_422(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        resp = client.post(f"/job-profiles/{jp['id']}/projects", json={
            "project_name": "Test", "start_month_year": "06/2023", "end_month_year": "01/2023"
        })
        assert resp.status_code == 422

    def test_invalid_date_format_422(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        resp = client.post(f"/job-profiles/{jp['id']}/projects", json={
            "project_name": "Test", "start_month_year": "2023-01"
        })
        assert resp.status_code == 422

    def test_html_stripped(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        proj = _add_project(client, jp["id"],
                            project_name="<script>alert(1)</script>My App")
        assert "<script>" not in proj["project_name"]

    def test_cross_user_returns_404(self, app, authenticated_client):
        client_a, _, _ = authenticated_client
        jp_a = _create_job_profile(client_a)

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
        async def override_b(): return user_b
        app.dependency_overrides[get_current_user] = override_b
        try:
            from fastapi.testclient import TestClient
            with TestClient(app) as client_b:
                resp = client_b.get(f"/job-profiles/{jp_a['id']}/projects")
                assert resp.status_code == 404
        finally:
            app.dependency_overrides.clear()


class TestImport:
    def _create_master_project(self, client):
        resp = client.post("/profile/projects", json={
            "project_name": "Master App", "description": "Master project",
            "start_month_year": "01/2023"
        })
        assert resp.status_code == 201
        return resp.json()

    def test_import_success(self, authenticated_client):
        client, _, _ = authenticated_client
        master = self._create_master_project(client)
        jp = _create_job_profile(client)
        resp = client.post(f"/job-profiles/{jp['id']}/projects/import",
                           json={"source_ids": [master["id"]]})
        assert resp.status_code == 200
        data = resp.json()
        assert master["id"] in data["imported"]
        assert data["skipped"] == []
        # Verify source_project_id set
        list_resp = client.get(f"/job-profiles/{jp['id']}/projects")
        assert list_resp.json()[0]["source_project_id"] == master["id"]

    def test_import_skips_duplicates(self, authenticated_client):
        client, _, _ = authenticated_client
        master = self._create_master_project(client)
        jp = _create_job_profile(client)
        client.post(f"/job-profiles/{jp['id']}/projects/import",
                    json={"source_ids": [master["id"]]})
        resp = client.post(f"/job-profiles/{jp['id']}/projects/import",
                           json={"source_ids": [master["id"]]})
        assert resp.status_code == 200
        assert master["id"] in resp.json()["skipped"]

    def test_import_cross_user_not_found(self, app, authenticated_client):
        client_a, _, _ = authenticated_client
        master = self._create_master_project(client_a)

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
        async def override_b(): return user_b
        app.dependency_overrides[get_current_user] = override_b
        try:
            from fastapi.testclient import TestClient
            with TestClient(app) as client_b:
                client_b.post("/profile")
                jp_b = client_b.post("/job-profiles", json={
                    "profile_name": f"B {uuid.uuid4().hex[:8]}"
                }).json()
                resp = client_b.post(f"/job-profiles/{jp_b['id']}/projects/import",
                                     json={"source_ids": [master["id"]]})
                assert resp.status_code == 200
                assert master["id"] in resp.json()["not_found"]
        finally:
            app.dependency_overrides.clear()

    def test_import_empty_ids_422(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        resp = client.post(f"/job-profiles/{jp['id']}/projects/import",
                           json={"source_ids": []})
        assert resp.status_code == 422

    def test_delete_master_nullifies_source_id(self, authenticated_client):
        client, _, _ = authenticated_client
        master = self._create_master_project(client)
        jp = _create_job_profile(client)
        client.post(f"/job-profiles/{jp['id']}/projects/import",
                    json={"source_ids": [master["id"]]})
        jp_proj_id = client.get(f"/job-profiles/{jp['id']}/projects").json()[0]["id"]
        client.delete(f"/profile/projects/{master['id']}")
        resp = client.get(f"/job-profiles/{jp['id']}/projects/{jp_proj_id}")
        assert resp.status_code == 200
        assert resp.json()["source_project_id"] is None


class TestB5Parity:
    """B5 parity tests: technologies JSONB field for job profile projects."""

    def test_technologies_field_roundtrip(self, authenticated_client):
        """B5: technologies list is stored and returned correctly."""
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        proj = _add_project(client, jp["id"], technologies=["Python", "FastAPI", "PostgreSQL"])
        assert proj["technologies"] == ["Python", "FastAPI", "PostgreSQL"]

    def test_technologies_defaults_empty(self, authenticated_client):
        """B5: technologies defaults to empty list when not provided."""
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        proj = _add_project(client, jp["id"])
        assert proj["technologies"] == []

    def test_technologies_update(self, authenticated_client):
        """B5: PATCH updates technologies correctly."""
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        proj = _add_project(client, jp["id"], technologies=["Python"])
        resp = client.patch(f"/job-profiles/{jp['id']}/projects/{proj['id']}", json={
            "technologies": ["Python", "Docker"],
        })
        assert resp.status_code == 200
        assert resp.json()["technologies"] == ["Python", "Docker"]

    def test_technologies_max_30_items(self, authenticated_client):
        """B5: More than 30 technologies returns 422."""
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        resp = client.post(f"/job-profiles/{jp['id']}/projects", json={
            "project_name": "Big Project",
            "technologies": [f"Tech{i}" for i in range(31)],
        })
        assert resp.status_code == 422

    def test_html_stripped_from_technologies(self, authenticated_client):
        """B5: HTML tags are stripped from technology items."""
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        proj = _add_project(client, jp["id"], technologies=["<b>Python</b>"])
        assert "<b>" not in proj["technologies"][0]
        assert "Python" in proj["technologies"][0]
