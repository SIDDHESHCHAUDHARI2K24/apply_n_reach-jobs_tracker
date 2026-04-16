"""Router for job opening ingestion endpoints."""
import json

import asyncpg
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.features.auth.utils import get_current_user
from app.features.core.config import get_settings
from app.features.core.dependencies import DbDep
from app.features.job_tracker.opening_ingestion.schemas import (
    ExtractedDetailsResponse,
    ExtractionRefreshResponse,
    ExtractionRunResponse,
)
from app.features.job_tracker.opening_ingestion.service import (
    check_in_flight,
    enqueue_extraction,
    get_latest_extracted_details,
    list_extraction_runs,
    run_extraction,
)

router = APIRouter(tags=["job-openings-extraction"])


@router.post(
    "/job-openings/{opening_id}/extraction/refresh",
    status_code=202,
    response_model=ExtractionRefreshResponse,
)
async def refresh_extraction(
    opening_id: int,
    background_tasks: BackgroundTasks,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> ExtractionRefreshResponse:
    """Enqueue a new extraction run. Returns 202 Accepted.

    Returns 409 if a run is already in-flight.
    """
    # Verify ownership
    opening = await conn.fetchrow(
        "SELECT id, source_url FROM job_openings WHERE id=$1 AND user_id=$2",
        opening_id,
        current_user["id"],
    )
    if not opening:
        raise HTTPException(status_code=404, detail="Job opening not found")
    if not opening["source_url"]:
        raise HTTPException(
            status_code=400, detail="Opening has no source URL to extract from"
        )

    # Check for in-flight
    if await check_in_flight(conn, opening_id):
        raise HTTPException(status_code=409, detail="Extraction already in progress")

    run = await enqueue_extraction(conn, opening_id)
    settings = get_settings()
    background_tasks.add_task(run_extraction, opening_id, run["id"], settings.database_url)

    return ExtractionRefreshResponse(message="Extraction queued", run_id=run["id"])


@router.get(
    "/job-openings/{opening_id}/extracted-details/latest",
    response_model=ExtractedDetailsResponse,
)
async def get_extracted_details(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> ExtractedDetailsResponse:
    """Get the most recent succeeded extraction snapshot for a job opening."""
    row = await get_latest_extracted_details(conn, current_user["id"], opening_id)

    # Handle JSONB fields
    required_skills = row["required_skills"]
    preferred_skills = row["preferred_skills"]
    if isinstance(required_skills, str):
        required_skills = json.loads(required_skills)
    if isinstance(preferred_skills, str):
        preferred_skills = json.loads(preferred_skills)

    return ExtractedDetailsResponse(
        **{
            k: v
            for k, v in dict(row).items()
            if k not in ("required_skills", "preferred_skills", "id", "version_id")
        },
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        extraction_run_id=row["run_id"],
    )


@router.get(
    "/job-openings/{opening_id}/extraction-runs",
    response_model=list[ExtractionRunResponse],
)
async def get_extraction_runs(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> list[ExtractionRunResponse]:
    """List all extraction runs for a job opening, newest first."""
    rows = await list_extraction_runs(conn, current_user["id"], opening_id)
    return [ExtractionRunResponse(**dict(r)) for r in rows]
