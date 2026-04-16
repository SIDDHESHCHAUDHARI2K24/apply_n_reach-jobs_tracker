"""Tests for idempotency of the ingestion pipeline (409 on duplicate enqueue)."""
import asyncio
import uuid

import asyncpg
import pytest

from app.features.core.config import settings


@pytest.mark.usefixtures("mock_crawl", "mock_extract")
def test_409_on_duplicate_refresh(auth_client, sample_opening):
    """Second POST to /extraction/refresh while first is queued returns 409."""
    client, _ = auth_client
    opening_id = sample_opening["id"]

    # First call should succeed
    resp1 = client.post(f"/job-openings/{opening_id}/extraction/refresh")
    assert resp1.status_code == 202, f"Expected 202, got {resp1.status_code}: {resp1.text}"

    # Second call should be rejected while first is in-flight
    # (Background task may already have run in test context, so we check the run status)
    async def check_and_update():
        conn = await asyncpg.connect(settings.database_url)
        try:
            run_id = resp1.json()["run_id"]
            run = await conn.fetchrow(
                "SELECT status FROM job_opening_extraction_runs WHERE id=$1", run_id
            )
            return run["status"] if run else None
        finally:
            await conn.close()

    run_status = asyncio.run(check_and_update())

    if run_status in ("queued", "running"):
        # Should get 409 since run is in-flight
        resp2 = client.post(f"/job-openings/{opening_id}/extraction/refresh")
        assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"
        assert "already in progress" in resp2.json()["detail"].lower()


@pytest.mark.usefixtures("mock_crawl", "mock_extract")
def test_409_while_queued(auth_client, sample_opening):
    """Directly insert a queued run then verify second API call returns 409."""
    client, _ = auth_client
    opening_id = sample_opening["id"]

    # Directly insert a queued run to simulate in-flight state
    async def insert_queued_run():
        conn = await asyncpg.connect(settings.database_url)
        try:
            run = await conn.fetchrow(
                """
                INSERT INTO job_opening_extraction_runs (opening_id, status, attempt_number)
                VALUES ($1, 'queued', 1)
                RETURNING id
                """,
                opening_id,
            )
            return run["id"]
        finally:
            await conn.close()

    run_id = asyncio.run(insert_queued_run())
    assert run_id is not None

    # API call should return 409
    resp = client.post(f"/job-openings/{opening_id}/extraction/refresh")
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"
    assert "already in progress" in resp.json()["detail"].lower()


@pytest.mark.usefixtures("mock_crawl", "mock_extract")
def test_202_after_previous_run_succeeded(auth_client, sample_opening):
    """Can enqueue new extraction after previous run is marked succeeded."""
    client, _ = auth_client
    opening_id = sample_opening["id"]

    # Insert a succeeded run
    async def insert_succeeded_run():
        conn = await asyncpg.connect(settings.database_url)
        try:
            run = await conn.fetchrow(
                """
                INSERT INTO job_opening_extraction_runs (opening_id, status, attempt_number)
                VALUES ($1, 'succeeded', 1)
                RETURNING id
                """,
                opening_id,
            )
            return run["id"]
        finally:
            await conn.close()

    asyncio.run(insert_succeeded_run())

    # Should be able to trigger a new extraction
    resp = client.post(f"/job-openings/{opening_id}/extraction/refresh")
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "run_id" in data
    assert data["message"] == "Extraction queued"


@pytest.mark.usefixtures("mock_crawl", "mock_extract")
def test_202_after_previous_run_failed(auth_client, sample_opening):
    """Can enqueue new extraction after previous run is marked failed."""
    client, _ = auth_client
    opening_id = sample_opening["id"]

    # Insert a failed run
    async def insert_failed_run():
        conn = await asyncpg.connect(settings.database_url)
        try:
            run = await conn.fetchrow(
                """
                INSERT INTO job_opening_extraction_runs (opening_id, status, attempt_number)
                VALUES ($1, 'failed', 1)
                RETURNING id
                """,
                opening_id,
            )
            return run["id"]
        finally:
            await conn.close()

    asyncio.run(insert_failed_run())

    # Should be able to trigger a new extraction
    resp = client.post(f"/job-openings/{opening_id}/extraction/refresh")
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "run_id" in data


@pytest.mark.usefixtures("mock_crawl", "mock_extract")
def test_409_while_running(auth_client, sample_opening):
    """Directly insert a running run then verify second API call returns 409."""
    client, _ = auth_client
    opening_id = sample_opening["id"]

    # Directly insert a running run
    async def insert_running_run():
        conn = await asyncpg.connect(settings.database_url)
        try:
            run = await conn.fetchrow(
                """
                INSERT INTO job_opening_extraction_runs
                    (opening_id, status, attempt_number, started_at)
                VALUES ($1, 'running', 1, NOW())
                RETURNING id
                """,
                opening_id,
            )
            return run["id"]
        finally:
            await conn.close()

    run_id = asyncio.run(insert_running_run())
    assert run_id is not None

    # API call should return 409
    resp = client.post(f"/job-openings/{opening_id}/extraction/refresh")
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"
