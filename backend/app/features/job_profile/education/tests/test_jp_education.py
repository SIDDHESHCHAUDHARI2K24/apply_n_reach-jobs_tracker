"""Integration tests for job_profile education endpoints."""
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


def _add_education(client, job_profile_id, **overrides):
    payload = {
        "university_name": "MIT",
        "major": "Computer Science",
        "degree_type": "BS",
        "start_month_year": "09/2018",
        "end_month_year": "06/2022",
        **overrides,
    }
    resp = client.post(f"/job-profiles/{job_profile_id}/education", json=payload)
    assert resp.status_code == 201
    return resp.json()


class TestListAndGet:
    def test_list_empty(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        resp = client.get(f"/job-profiles/{jp['id']}/education")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_add_and_list(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        _add_education(client, jp["id"])
        _add_education(client, jp["id"], university_name="Stanford", major="AI", degree_type="MS",
                       start_month_year="09/2022", end_month_year=None)
        resp = client.get(f"/job-profiles/{jp['id']}/education")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_by_id(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        edu = _add_education(client, jp["id"])
        resp = client.get(f"/job-profiles/{jp['id']}/education/{edu['id']}")
        assert resp.status_code == 200
        assert resp.json()["university_name"] == "MIT"

    def test_get_nonexistent_404(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        resp = client.get(f"/job-profiles/{jp['id']}/education/99999")
        assert resp.status_code == 404

    def test_unauthenticated_401(self, client):
        resp = client.get("/job-profiles/1/education")
        assert resp.status_code == 401


class TestCRUD:
    def test_delete(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        edu = _add_education(client, jp["id"])
        resp = client.delete(f"/job-profiles/{jp['id']}/education/{edu['id']}")
        assert resp.status_code == 204
        resp = client.get(f"/job-profiles/{jp['id']}/education/{edu['id']}")
        assert resp.status_code == 404

    def test_partial_update_single_field(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        edu = _add_education(client, jp["id"])
        resp = client.patch(f"/job-profiles/{jp['id']}/education/{edu['id']}", json={
            "major": "Electrical Engineering"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["major"] == "Electrical Engineering"
        assert data["university_name"] == "MIT"  # unchanged

    def test_partial_update_empty_body_400(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        edu = _add_education(client, jp["id"])
        resp = client.patch(f"/job-profiles/{jp['id']}/education/{edu['id']}", json={})
        assert resp.status_code == 400

    def test_source_education_id_null_for_manual_entry(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        edu = _add_education(client, jp["id"])
        assert edu["source_education_id"] is None

    def test_jsonb_fields_roundtrip(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        edu = _add_education(client, jp["id"],
                             bullet_points=["Dean's list", "Robotics club"],
                             reference_links=["https://mit.edu/transcript"])
        assert edu["bullet_points"] == ["Dean's list", "Robotics club"]
        assert edu["reference_links"] == ["https://mit.edu/transcript"]


class TestValidation:
    def test_end_before_start_422(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        resp = client.post(f"/job-profiles/{jp['id']}/education", json={
            "university_name": "MIT", "major": "CS", "degree_type": "BS",
            "start_month_year": "09/2022", "end_month_year": "06/2021"
        })
        assert resp.status_code == 422

    def test_invalid_date_format_422(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        resp = client.post(f"/job-profiles/{jp['id']}/education", json={
            "university_name": "MIT", "major": "CS", "degree_type": "BS",
            "start_month_year": "2022-09"
        })
        assert resp.status_code == 422

    def test_html_stripped(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        edu = _add_education(client, jp["id"],
                             university_name="<script>alert(1)</script>MIT")
        assert "<script>" not in edu["university_name"]

    def test_cross_user_returns_404(self, app, authenticated_client):
        client_a, _, _ = authenticated_client
        jp_a = _create_job_profile(client_a)
        _add_education(client_a, jp_a["id"])

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
            from fastapi.testclient import TestClient
            with TestClient(app) as client_b:
                resp = client_b.get(f"/job-profiles/{jp_a['id']}/education")
                assert resp.status_code == 404
        finally:
            app.dependency_overrides.clear()


class TestImport:
    def _create_master_education(self, client):
        resp = client.post("/profile/education", json={
            "university_name": "MIT", "major": "CS", "degree_type": "BS",
            "start_month_year": "09/2018", "end_month_year": "06/2022"
        })
        assert resp.status_code == 201
        return resp.json()

    def test_import_success(self, authenticated_client):
        client, _, _ = authenticated_client
        master_edu = self._create_master_education(client)
        jp = _create_job_profile(client)
        resp = client.post(f"/job-profiles/{jp['id']}/education/import",
                           json={"source_ids": [master_edu["id"]]})
        assert resp.status_code == 200
        data = resp.json()
        assert master_edu["id"] in data["imported"]
        assert data["skipped"] == []
        assert data["not_found"] == []
        # Verify the imported entry has source_education_id set
        list_resp = client.get(f"/job-profiles/{jp['id']}/education")
        assert list_resp.json()[0]["source_education_id"] == master_edu["id"]

    def test_import_skips_duplicates(self, authenticated_client):
        client, _, _ = authenticated_client
        master_edu = self._create_master_education(client)
        jp = _create_job_profile(client)
        client.post(f"/job-profiles/{jp['id']}/education/import",
                    json={"source_ids": [master_edu["id"]]})
        resp = client.post(f"/job-profiles/{jp['id']}/education/import",
                           json={"source_ids": [master_edu["id"]]})
        assert resp.status_code == 200
        data = resp.json()
        assert master_edu["id"] in data["skipped"]
        assert data["imported"] == []

    def test_import_cross_user_not_found(self, app, authenticated_client):
        client_a, _, _ = authenticated_client
        master_edu = self._create_master_education(client_a)
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

        async def override_b():
            return user_b

        app.dependency_overrides[get_current_user] = override_b
        try:
            from fastapi.testclient import TestClient
            with TestClient(app) as client_b:
                # User B creates their own profile and job profile
                client_b.post("/profile")
                jp_b_resp = client_b.post("/job-profiles", json={
                    "profile_name": f"B Profile {uuid.uuid4().hex[:8]}"
                })
                jp_b = jp_b_resp.json()
                # User B tries to import User A's education
                resp = client_b.post(f"/job-profiles/{jp_b['id']}/education/import",
                                     json={"source_ids": [master_edu["id"]]})
                assert resp.status_code == 200
                data = resp.json()
                assert master_edu["id"] in data["not_found"]
                assert data["imported"] == []
        finally:
            app.dependency_overrides.clear()

    def test_import_empty_ids_422(self, authenticated_client):
        client, _, _ = authenticated_client
        jp = _create_job_profile(client)
        resp = client.post(f"/job-profiles/{jp['id']}/education/import",
                           json={"source_ids": []})
        assert resp.status_code == 422

    def test_delete_master_nullifies_source_id(self, authenticated_client):
        client, _, _ = authenticated_client
        master_edu = self._create_master_education(client)
        jp = _create_job_profile(client)
        client.post(f"/job-profiles/{jp['id']}/education/import",
                    json={"source_ids": [master_edu["id"]]})
        # Get the job profile education entry
        list_resp = client.get(f"/job-profiles/{jp['id']}/education")
        jp_edu_id = list_resp.json()[0]["id"]
        # Delete master education
        client.delete(f"/profile/education/{master_edu['id']}")
        # Job profile education should still exist with source_education_id=null
        resp = client.get(f"/job-profiles/{jp['id']}/education/{jp_edu_id}")
        assert resp.status_code == 200
        assert resp.json()["source_education_id"] is None
