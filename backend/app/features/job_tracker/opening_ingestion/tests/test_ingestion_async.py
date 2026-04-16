"""Tests for the async ingestion pipeline success flow."""
import asyncio
import time

import asyncpg
import pytest

from app.features.core.config import settings
from app.features.job_tracker.opening_ingestion.service import run_extraction


@pytest.mark.usefixtures("mock_crawl", "mock_extract")
def test_refresh_extraction_returns_202(auth_client, sample_opening):
    """POST /job-openings/{id}/extraction/refresh returns 202 with run_id."""
    client, _ = auth_client
    opening_id = sample_opening["id"]

    resp = client.post(f"/job-openings/{opening_id}/extraction/refresh")
    assert resp.status_code == 202
    data = resp.json()
    assert "run_id" in data
    assert data["message"] == "Extraction queued"
    assert isinstance(data["run_id"], int)


@pytest.mark.usefixtures("mock_crawl", "mock_extract")
def test_refresh_extraction_background_completes(auth_client, sample_opening):
    """Verify extraction run eventually has status=succeeded and version row exists."""
    client, _ = auth_client
    opening_id = sample_opening["id"]

    # Trigger extraction
    resp = client.post(f"/job-openings/{opening_id}/extraction/refresh")
    assert resp.status_code == 202
    run_id = resp.json()["run_id"]

    # Background task runs synchronously in TestClient context; check DB state
    async def check_db():
        conn = await asyncpg.connect(settings.database_url)
        try:
            # Wait up to 5 seconds for the background task to complete
            for _ in range(50):
                run = await conn.fetchrow(
                    "SELECT status FROM job_opening_extraction_runs WHERE id=$1", run_id
                )
                if run and run["status"] == "succeeded":
                    break
                await asyncio.sleep(0.1)

            run = await conn.fetchrow(
                "SELECT * FROM job_opening_extraction_runs WHERE id=$1", run_id
            )
            assert run is not None
            assert run["status"] == "succeeded", f"Expected succeeded, got {run['status']}: {run['error_message']}"

            version = await conn.fetchrow(
                "SELECT * FROM job_opening_extracted_details_versions WHERE run_id=$1", run_id
            )
            assert version is not None
            assert version["job_title"] == "Software Engineer"
            assert version["company_name"] == "Acme Corp"
            return run, version
        finally:
            await conn.close()

    asyncio.run(check_db())


@pytest.mark.usefixtures("mock_crawl", "mock_extract")
def test_get_extracted_details_latest(auth_client, sample_opening):
    """GET /job-openings/{id}/extracted-details/latest returns extracted data after success."""
    client, _ = auth_client
    opening_id = sample_opening["id"]

    # Trigger extraction and wait for it to complete
    resp = client.post(f"/job-openings/{opening_id}/extraction/refresh")
    assert resp.status_code == 202
    run_id = resp.json()["run_id"]

    # Wait for completion
    async def wait_for_completion():
        conn = await asyncpg.connect(settings.database_url)
        try:
            for _ in range(50):
                run = await conn.fetchrow(
                    "SELECT status FROM job_opening_extraction_runs WHERE id=$1", run_id
                )
                if run and run["status"] in ("succeeded", "failed"):
                    break
                await asyncio.sleep(0.1)
        finally:
            await conn.close()

    asyncio.run(wait_for_completion())

    # Now fetch the latest details
    resp = client.get(f"/job-openings/{opening_id}/extracted-details/latest")
    assert resp.status_code == 200
    data = resp.json()
    assert data["job_title"] == "Software Engineer"
    assert data["company_name"] == "Acme Corp"
    assert data["opening_id"] == opening_id
    assert "extraction_run_id" in data
    assert "extracted_at" in data
    assert isinstance(data["required_skills"], list)


@pytest.mark.usefixtures("mock_crawl", "mock_extract")
def test_get_extraction_runs_returns_history(auth_client, sample_opening):
    """GET /job-openings/{id}/extraction-runs returns run history."""
    client, _ = auth_client
    opening_id = sample_opening["id"]

    # Trigger extraction
    resp = client.post(f"/job-openings/{opening_id}/extraction/refresh")
    assert resp.status_code == 202
    run_id = resp.json()["run_id"]

    # Wait for completion
    async def wait_for_completion():
        conn = await asyncpg.connect(settings.database_url)
        try:
            for _ in range(50):
                run = await conn.fetchrow(
                    "SELECT status FROM job_opening_extraction_runs WHERE id=$1", run_id
                )
                if run and run["status"] in ("succeeded", "failed"):
                    break
                await asyncio.sleep(0.1)
        finally:
            await conn.close()

    asyncio.run(wait_for_completion())

    resp = client.get(f"/job-openings/{opening_id}/extraction-runs")
    assert resp.status_code == 200
    runs = resp.json()
    assert isinstance(runs, list)
    assert len(runs) >= 1
    run_ids = [r["id"] for r in runs]
    assert run_id in run_ids


def test_get_extracted_details_404_before_extraction(auth_client, sample_opening):
    """GET /extracted-details/latest returns 404 when no extraction has been run."""
    client, _ = auth_client
    opening_id = sample_opening["id"]

    resp = client.get(f"/job-openings/{opening_id}/extracted-details/latest")
    assert resp.status_code == 404


def test_refresh_extraction_404_no_source_url(auth_client):
    """POST refresh returns 400 for opening without source_url."""
    client, _ = auth_client

    # Create opening without source_url
    resp = client.post(
        "/job-openings",
        json={
            "company_name": "No URL Corp",
            "role_name": "Engineer",
        },
    )
    assert resp.status_code == 201
    opening_id = resp.json()["id"]

    resp = client.post(f"/job-openings/{opening_id}/extraction/refresh")
    assert resp.status_code == 400


def test_refresh_extraction_404_wrong_user(auth_client, sample_opening, app):
    """POST refresh returns 404 for opening belonging to another user."""
    # Create a second user
    import uuid
    import asyncpg as apg
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import hash_password, get_current_user

    async def create_second_user():
        conn = await apg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            email = f"other-{uuid.uuid4().hex}@example.com"
            user = await create_user(conn, email=email, password_hash=hash_password("pass"))
            return dict(user)
        finally:
            await conn.close()

    other_user = asyncio.run(create_second_user())

    async def override_other_user():
        return other_user

    app.dependency_overrides[get_current_user] = override_other_user

    from fastapi.testclient import TestClient
    with TestClient(app) as other_client:
        resp = other_client.post(
            f"/job-openings/{sample_opening['id']}/extraction/refresh"
        )
        assert resp.status_code == 404

    app.dependency_overrides.clear()
