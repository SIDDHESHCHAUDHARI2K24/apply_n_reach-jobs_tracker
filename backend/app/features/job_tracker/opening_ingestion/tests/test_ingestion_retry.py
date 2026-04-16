"""Tests for the retry logic in the ingestion pipeline."""
import asyncio
import uuid
from unittest.mock import AsyncMock, patch, call

import asyncpg
import pytest

from app.features.core.config import settings
from app.features.auth.models import ensure_auth_schema, create_user
from app.features.auth.utils import hash_password
from app.features.job_tracker.opening_ingestion.clients.apify_client import CrawlError
from app.features.job_tracker.opening_ingestion.service import _execute_run
from app.features.job_tracker.schemas import ExtractedJobDetails


SAMPLE_EXTRACTED = ExtractedJobDetails(
    job_title="Software Engineer",
    company_name="Retry Corp",
    location="New York, NY",
    employment_type="Full-time",
    required_skills=["Python"],
    extractor_model="claude-haiku-4-5-20251001",
    source_url="https://example.com/jobs/retry-test",
)


async def setup_test_opening(source_url: str = "https://example.com/jobs/retry-test"):
    """Create a test user and opening directly in the DB."""
    conn = await asyncpg.connect(settings.database_url)
    try:
        await ensure_auth_schema(conn)
        email = f"retry-test-{uuid.uuid4().hex}@example.com"
        user = await create_user(conn, email=email, password_hash=hash_password("pass"))
        user_id = user["id"]

        opening = await conn.fetchrow(
            """
            INSERT INTO job_openings (user_id, company_name, role_name, current_status, source_url)
            VALUES ($1, $2, $3, 'Interested', $4)
            RETURNING *
            """,
            user_id,
            f"Retry Corp {uuid.uuid4().hex[:8]}",
            "Software Engineer",
            source_url,
        )
        return user_id, opening["id"]
    finally:
        await conn.close()


async def get_runs_for_opening(conn, opening_id: int):
    """Fetch all extraction runs for an opening."""
    return await conn.fetch(
        "SELECT * FROM job_opening_extraction_runs WHERE opening_id=$1 ORDER BY attempt_number",
        opening_id,
    )


def test_retry_on_crawl_failure_then_success():
    """First crawl fails, second succeeds — verify retry creates attempt 2 and succeeds."""
    user_id, opening_id = asyncio.run(setup_test_opening())

    # Mock crawl: fail on first call, succeed on second
    crawl_call_count = 0

    async def flaky_crawl(url: str) -> str:
        nonlocal crawl_call_count
        crawl_call_count += 1
        if crawl_call_count == 1:
            raise CrawlError("Simulated crawl failure")
        return "Job posting content"

    async def run_test():
        conn = await asyncpg.connect(settings.database_url)
        try:
            # Create initial run
            run = await conn.fetchrow(
                """
                INSERT INTO job_opening_extraction_runs (opening_id, status, attempt_number)
                VALUES ($1, 'queued', 1)
                RETURNING id
                """,
                opening_id,
            )
            run_id = run["id"]

            with patch(
                "app.features.job_tracker.opening_ingestion.service.crawl_url",
                side_effect=flaky_crawl,
            ), patch(
                "app.features.job_tracker.opening_ingestion.service.extract_job_details",
                new_callable=AsyncMock,
                return_value=SAMPLE_EXTRACTED,
            ), patch("asyncio.sleep", new_callable=AsyncMock):
                await _execute_run(conn, opening_id, run_id)

            # Verify run history
            runs = await get_runs_for_opening(conn, opening_id)
            assert len(runs) == 2, f"Expected 2 runs, got {len(runs)}"

            run1 = next(r for r in runs if r["attempt_number"] == 1)
            run2 = next(r for r in runs if r["attempt_number"] == 2)

            assert run1["status"] == "failed", f"Run 1 should be failed, got {run1['status']}"
            assert run2["status"] == "succeeded", f"Run 2 should be succeeded, got {run2['status']}"
            assert run2["error_message"] is None or run1["error_message"] is not None

        finally:
            await conn.close()

    asyncio.run(run_test())


def test_retry_creates_correct_attempt_number():
    """Verify attempt_number increments correctly across retries."""
    user_id, opening_id = asyncio.run(setup_test_opening())

    call_count = 0

    async def always_fail_crawl(url: str) -> str:
        nonlocal call_count
        call_count += 1
        raise CrawlError(f"Failure on attempt {call_count}")

    async def run_test():
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
            run_id = run["id"]

            with patch(
                "app.features.job_tracker.opening_ingestion.service.crawl_url",
                side_effect=always_fail_crawl,
            ), patch(
                "app.features.job_tracker.opening_ingestion.service.extract_job_details",
                new_callable=AsyncMock,
            ), patch("asyncio.sleep", new_callable=AsyncMock):
                await _execute_run(conn, opening_id, run_id)

            runs = await get_runs_for_opening(conn, opening_id)
            attempt_numbers = sorted([r["attempt_number"] for r in runs])
            # Should have 3 attempts (MAX_ATTEMPTS = 3)
            assert attempt_numbers == [1, 2, 3], f"Expected [1, 2, 3], got {attempt_numbers}"

            # All should be failed
            for run in runs:
                assert run["status"] == "failed", f"Run {run['attempt_number']} should be failed"

        finally:
            await conn.close()

    asyncio.run(run_test())


def test_retry_skips_sleep_when_mocked():
    """Verify asyncio.sleep is called with retry delay but can be mocked to be instant."""
    user_id, opening_id = asyncio.run(setup_test_opening())

    async def run_test():
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
            run_id = run["id"]

            mock_sleep = AsyncMock()

            with patch(
                "app.features.job_tracker.opening_ingestion.service.crawl_url",
                new_callable=AsyncMock,
                side_effect=CrawlError("Always fails"),
            ), patch(
                "app.features.job_tracker.opening_ingestion.service.extract_job_details",
                new_callable=AsyncMock,
            ), patch("app.features.job_tracker.opening_ingestion.service.asyncio.sleep", mock_sleep):
                await _execute_run(conn, opening_id, run_id)

            # asyncio.sleep should have been called for retries (MAX_ATTEMPTS - 1 = 2 times)
            assert mock_sleep.call_count == 2, f"Expected 2 sleep calls, got {mock_sleep.call_count}"

        finally:
            await conn.close()

    asyncio.run(run_test())


def test_no_source_url_fails_immediately():
    """Opening with no source_url should fail immediately without retry."""
    user_id, opening_id = asyncio.run(setup_test_opening(source_url=None))

    async def run_test():
        conn = await asyncpg.connect(settings.database_url)
        try:
            # Update opening to have no source_url
            await conn.execute(
                "UPDATE job_openings SET source_url=NULL WHERE id=$1", opening_id
            )

            run = await conn.fetchrow(
                """
                INSERT INTO job_opening_extraction_runs (opening_id, status, attempt_number)
                VALUES ($1, 'queued', 1)
                RETURNING id
                """,
                opening_id,
            )
            run_id = run["id"]

            await _execute_run(conn, opening_id, run_id)

            run_result = await conn.fetchrow(
                "SELECT * FROM job_opening_extraction_runs WHERE id=$1", run_id
            )
            assert run_result["status"] == "failed"
            assert "No source URL" in run_result["error_message"]

            # Only one run should exist
            runs = await get_runs_for_opening(conn, opening_id)
            assert len(runs) == 1

        finally:
            await conn.close()

    asyncio.run(run_test())
