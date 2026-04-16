"""Service layer for job opening ingestion pipeline."""
import asyncio
import json
from datetime import datetime, timedelta, timezone

import asyncpg
from fastapi import HTTPException

from app.features.job_tracker.opening_ingestion.clients.apify_client import CrawlError, crawl_url
from app.features.job_tracker.opening_ingestion.clients.extraction_chain import (
    ExtractionError,
    extract_job_details,
)

RETRY_DELAYS = [30, 120]  # seconds between retry attempts
MAX_ATTEMPTS = 3  # 1 initial + 2 retries
STALE_RUN_THRESHOLD_MINUTES = 5


async def enqueue_extraction(conn, opening_id: int) -> asyncpg.Record:
    """Insert a new extraction run with status=queued. Returns the run row."""
    row = await conn.fetchrow(
        """
        INSERT INTO job_opening_extraction_runs (opening_id, status, attempt_number)
        VALUES ($1, 'queued', 1)
        RETURNING *
        """,
        opening_id,
    )
    return row


async def check_in_flight(conn, opening_id: int) -> bool:
    """Return True if there is a queued or running run for this opening."""
    row = await conn.fetchrow(
        """
        SELECT id FROM job_opening_extraction_runs
        WHERE opening_id = $1 AND status IN ('queued', 'running')
        LIMIT 1
        """,
        opening_id,
    )
    return row is not None


async def run_extraction(opening_id: int, run_id: int, db_url: str) -> None:
    """Background worker: executes the extraction pipeline.

    Opens its own DB connection since this runs outside the request lifecycle.
    Steps:
    1. Mark run as running
    2. Get source_url from job_openings
    3. crawl_url (60s timeout)
    4. extract_job_details
    5. Persist snapshot, mark succeeded
    On failure: retry up to MAX_ATTEMPTS with exponential backoff.
    """
    conn = await asyncpg.connect(db_url)
    try:
        await _execute_run(conn, opening_id, run_id)
    finally:
        await conn.close()


async def _execute_run(conn, opening_id: int, run_id: int) -> None:
    """Execute a single extraction run, handling retry logic."""
    # Mark as running
    await conn.execute(
        "UPDATE job_opening_extraction_runs SET status='running', started_at=NOW() WHERE id=$1",
        run_id,
    )

    # Get source_url
    opening = await conn.fetchrow(
        "SELECT source_url FROM job_openings WHERE id=$1", opening_id
    )
    if not opening or not opening["source_url"]:
        await _mark_failed(conn, run_id, "No source URL available")
        return

    # Get current attempt number
    run = await conn.fetchrow(
        "SELECT attempt_number FROM job_opening_extraction_runs WHERE id=$1", run_id
    )
    attempt = run["attempt_number"]

    try:
        # Crawl with timeout
        raw_text = await asyncio.wait_for(crawl_url(opening["source_url"]), timeout=60.0)

        # Extract structured data
        extracted = await extract_job_details(raw_text)

        # Persist snapshot
        await conn.execute(
            """
            INSERT INTO job_opening_extracted_details_versions (
                run_id, opening_id, schema_version,
                job_title, company_name, location, employment_type, salary_range,
                description_summary, required_skills, preferred_skills,
                experience_level, posted_date, application_deadline,
                raw_payload, extractor_model, source_url
            ) VALUES (
                $1, $2, 1,
                $3, $4, $5, $6, $7,
                $8, $9::jsonb, $10::jsonb,
                $11, $12, $13,
                $14::jsonb, $15, $16
            )
            """,
            run_id,
            opening_id,
            extracted.job_title,
            extracted.company_name,
            extracted.location,
            extracted.employment_type,
            extracted.salary_range,
            extracted.description_summary,
            json.dumps(extracted.required_skills or []),
            json.dumps(extracted.preferred_skills or []),
            extracted.experience_level,
            extracted.posted_date,
            extracted.application_deadline,
            json.dumps(extracted.model_dump()),
            extracted.extractor_model or "claude-haiku-4-5-20251001",
            extracted.source_url or opening["source_url"],
        )

        # Mark succeeded
        await conn.execute(
            "UPDATE job_opening_extraction_runs SET status='succeeded', completed_at=NOW() WHERE id=$1",
            run_id,
        )

    except (CrawlError, ExtractionError, asyncio.TimeoutError) as e:
        error_msg = str(e)
        if attempt < MAX_ATTEMPTS:
            # Schedule retry
            delay = RETRY_DELAYS[attempt - 1] if attempt - 1 < len(RETRY_DELAYS) else RETRY_DELAYS[-1]
            next_retry = datetime.now(timezone.utc) + timedelta(seconds=delay)

            # Create a new run for the retry
            new_run = await conn.fetchrow(
                """
                INSERT INTO job_opening_extraction_runs
                    (opening_id, status, attempt_number, next_retry_at, error_message)
                VALUES ($1, 'queued', $2, $3, $4)
                RETURNING id
                """,
                opening_id,
                attempt + 1,
                next_retry,
                error_msg,
            )

            # Mark current run as failed (not final failure)
            await conn.execute(
                "UPDATE job_opening_extraction_runs SET status='failed', completed_at=NOW(), error_message=$1 WHERE id=$2",
                error_msg,
                run_id,
            )

            # Wait for retry delay then execute
            await asyncio.sleep(delay)
            await _execute_run(conn, opening_id, new_run["id"])
        else:
            await _mark_failed(conn, run_id, error_msg)


async def _mark_failed(conn, run_id: int, error_msg: str) -> None:
    """Mark a run as failed with an error message."""
    await conn.execute(
        "UPDATE job_opening_extraction_runs SET status='failed', completed_at=NOW(), error_message=$1 WHERE id=$2",
        error_msg,
        run_id,
    )


async def get_latest_extracted_details(conn, user_id: int, opening_id: int):
    """Get most recent succeeded extraction snapshot for an opening."""
    # Verify ownership
    opening = await conn.fetchrow(
        "SELECT id FROM job_openings WHERE id=$1 AND user_id=$2", opening_id, user_id
    )
    if not opening:
        raise HTTPException(status_code=404, detail="Job opening not found")

    row = await conn.fetchrow(
        """
        SELECT v.*, v.id AS version_id FROM job_opening_extracted_details_versions v
        JOIN job_opening_extraction_runs r ON r.id = v.run_id
        WHERE v.opening_id = $1 AND r.status = 'succeeded'
        ORDER BY v.extracted_at DESC
        LIMIT 1
        """,
        opening_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="No extraction results available")
    return row


async def list_extraction_runs(conn, user_id: int, opening_id: int):
    """List all extraction runs for an opening, newest first."""
    opening = await conn.fetchrow(
        "SELECT id FROM job_openings WHERE id=$1 AND user_id=$2", opening_id, user_id
    )
    if not opening:
        raise HTTPException(status_code=404, detail="Job opening not found")

    rows = await conn.fetch(
        "SELECT * FROM job_opening_extraction_runs WHERE opening_id=$1 ORDER BY created_at DESC",
        opening_id,
    )
    return rows


async def startup_stale_run_cleanup(conn) -> int:
    """Mark running runs older than 5 minutes as failed (handles server restart)."""
    result = await conn.execute(
        """
        UPDATE job_opening_extraction_runs
        SET status='failed', completed_at=NOW(),
            error_message='Marked failed on startup: run was stale (server restart)'
        WHERE status='running'
          AND started_at < NOW() - INTERVAL '5 minutes'
        """,
    )
    count = int(result.split()[-1])
    return count
