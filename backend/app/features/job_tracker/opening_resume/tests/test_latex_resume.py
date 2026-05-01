"""Integration tests for opening_resume LaTeX endpoints."""

import asyncio
import shutil
import uuid

import asyncpg
import pytest
from fastapi.testclient import TestClient

from app.features.auth.models import create_user, ensure_auth_schema
from app.features.auth.utils import get_current_user, hash_password
from app.features.core.config import settings

pdflatex_available = shutil.which("pdflatex") is not None
skip_no_pdflatex = pytest.mark.skipif(
    not pdflatex_available,
    reason="pdflatex not installed",
)


async def _count_rows(query: str, *args):
    """Run a COUNT query and return the integer result."""
    conn = await asyncpg.connect(settings.database_url)
    try:
        return await conn.fetchval(query, *args)
    finally:
        await conn.close()


async def _count_job_profile_rendered_resume_rows(job_profile_id: int) -> int:
    """Count rows in job_profile rendered_resume table for one profile."""
    conn = await asyncpg.connect(settings.database_url)
    try:
        table_exists = await conn.fetchval(
            "SELECT to_regclass('public.rendered_resume') IS NOT NULL"
        )
        if not table_exists:
            return 0
        return await conn.fetchval(
            "SELECT COUNT(*) FROM rendered_resume WHERE job_profile_id = $1",
            job_profile_id,
        )
    finally:
        await conn.close()


async def _create_user_b() -> dict:
    """Create and return a second user for isolation tests."""
    conn = await asyncpg.connect(settings.database_url)
    try:
        await ensure_auth_schema(conn)
        email = f"test-opening-latex-b-{uuid.uuid4().hex}@example.com"
        user = await create_user(conn, email=email, password_hash=hash_password("testpass"))
        return dict(user)
    finally:
        await conn.close()


class TestRenderEndpoint:
    @skip_no_pdflatex
    def test_render_success_defaults_and_domain_boundary(
        self, auth_client, sample_opening, sample_resume, sample_job_profile
    ):
        client, _ = auth_client
        opening_id = sample_opening["id"]

        pre_job_profile_count = asyncio.run(
            _count_job_profile_rendered_resume_rows(sample_job_profile["id"])
        )

        resp = client.post(f"/job-openings/{opening_id}/resume/latex-resume/render")
        assert resp.status_code == 200
        body = resp.json()

        assert body["resume_id"] == sample_resume["id"]
        assert body["template_name"] == "jakes_resume_v1"
        assert "updated_at" in body
        assert body["latex_length"] > 0
        assert body["pdf_size_bytes"] > 0

        post_job_profile_count = asyncio.run(
            _count_job_profile_rendered_resume_rows(sample_job_profile["id"])
        )
        assert post_job_profile_count == pre_job_profile_count

    @skip_no_pdflatex
    def test_render_upsert_overwrites_same_row(self, auth_client, sample_opening, sample_resume):
        client, _ = auth_client
        opening_id = sample_opening["id"]
        render_path = f"/job-openings/{opening_id}/resume/latex-resume/render"

        resp1 = client.post(render_path)
        assert resp1.status_code == 200
        resp2 = client.post(render_path, json={"layout": {"body_font_size_pt": 11}})
        assert resp2.status_code == 200

        body1 = resp1.json()
        body2 = resp2.json()
        assert body1["resume_id"] == sample_resume["id"]
        assert body2["resume_id"] == sample_resume["id"]

        rendered_rows = asyncio.run(
            _count_rows(
                "SELECT COUNT(*) FROM job_opening_rendered_resumes WHERE resume_id = $1",
                sample_resume["id"],
            )
        )
        assert rendered_rows == 1


class TestMetadataEndpoint:
    def test_metadata_404_before_render(self, auth_client, sample_opening):
        client, _ = auth_client
        resp = client.get(f"/job-openings/{sample_opening['id']}/resume/latex-resume")
        assert resp.status_code == 404

    @skip_no_pdflatex
    def test_metadata_200_after_render(self, auth_client, sample_opening, sample_resume):
        client, _ = auth_client
        opening_id = sample_opening["id"]
        client.post(f"/job-openings/{opening_id}/resume/latex-resume/render")

        resp = client.get(f"/job-openings/{opening_id}/resume/latex-resume")
        assert resp.status_code == 200
        body = resp.json()
        assert body["resume_id"] == sample_resume["id"]
        assert body["template_name"] == "jakes_resume_v1"
        assert "updated_at" in body
        assert body["latex_length"] > 0
        assert body["pdf_size_bytes"] > 0


class TestPdfEndpoint:
    def test_pdf_404_before_render(self, auth_client, sample_opening):
        client, _ = auth_client
        resp = client.get(f"/job-openings/{sample_opening['id']}/resume/latex-resume/pdf")
        assert resp.status_code == 404

    @skip_no_pdflatex
    def test_pdf_200_after_render(self, auth_client, sample_opening):
        client, _ = auth_client
        opening_id = sample_opening["id"]
        client.post(f"/job-openings/{opening_id}/resume/latex-resume/render")

        resp = client.get(f"/job-openings/{opening_id}/resume/latex-resume/pdf")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert "content-disposition" in resp.headers
        assert resp.content[:4] == b"%PDF"

    @skip_no_pdflatex
    def test_pdf_filename_is_stable_after_personal_updates(
        self, auth_client, sample_opening, sample_resume
    ):
        client, _ = auth_client
        opening_id = sample_opening["id"]
        client.post(f"/job-openings/{opening_id}/resume/latex-resume/render")

        first_resp = client.get(f"/job-openings/{opening_id}/resume/latex-resume/pdf")
        assert first_resp.status_code == 200
        first_disposition = first_resp.headers["content-disposition"]

        # Mutate personal data after render; filename should remain stable.
        put_resp = client.put(
            f"/job-openings/{opening_id}/resume/personal",
            json={"full_name": "Renamed User", "email": "renamed@example.com"},
        )
        assert put_resp.status_code == 200

        second_resp = client.get(f"/job-openings/{opening_id}/resume/latex-resume/pdf")
        assert second_resp.status_code == 200
        second_disposition = second_resp.headers["content-disposition"]

        expected_filename = f'attachment; filename="opening_{opening_id}_resume_{sample_resume["id"]}.pdf"'
        assert first_disposition == expected_filename
        assert second_disposition == expected_filename


class TestAuthEndpoints:
    def test_401_render_without_auth(self, app):
        with TestClient(app) as client:
            resp = client.post("/job-openings/1/resume/latex-resume/render")
        assert resp.status_code == 401

    def test_401_metadata_without_auth(self, app):
        with TestClient(app) as client:
            resp = client.get("/job-openings/1/resume/latex-resume")
        assert resp.status_code == 401

    def test_401_pdf_without_auth(self, app):
        with TestClient(app) as client:
            resp = client.get("/job-openings/1/resume/latex-resume/pdf")
        assert resp.status_code == 401


class TestCrossUserIsolation:
    def test_user_b_cannot_render_for_user_a_opening(
        self, app, auth_client, sample_opening, sample_resume
    ):
        user_b = asyncio.run(_create_user_b())

        async def override_b():
            return user_b

        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.post(
                f"/job-openings/{sample_opening['id']}/resume/latex-resume/render"
            )
        app.dependency_overrides.clear()

        assert resp.status_code == 404

    @skip_no_pdflatex
    def test_user_b_cannot_read_metadata_or_pdf_for_user_a_opening(
        self, app, auth_client, sample_opening, sample_resume
    ):
        client_a, _ = auth_client
        opening_id = sample_opening["id"]
        client_a.post(f"/job-openings/{opening_id}/resume/latex-resume/render")

        user_b = asyncio.run(_create_user_b())

        async def override_b():
            return user_b

        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            metadata_resp = client_b.get(f"/job-openings/{opening_id}/resume/latex-resume")
            assert metadata_resp.status_code == 404

            pdf_resp = client_b.get(f"/job-openings/{opening_id}/resume/latex-resume/pdf")
            assert pdf_resp.status_code == 404
        app.dependency_overrides.clear()
