"""Router for job opening resume snapshot endpoints."""
import asyncpg
from fastapi import APIRouter, Depends, Query, status

from app.features.core.dependencies import DbDep
from app.features.auth.utils import get_current_user
from app.features.job_tracker.opening_resume import service
from app.features.job_tracker.opening_resume.schemas import ResumeResponse

router = APIRouter(tags=["job-opening-resume"])


@router.post(
    "/job-openings/{opening_id}/resume",
    response_model=ResumeResponse,
    status_code=201,
)
async def create_resume_snapshot(
    opening_id: int,
    source_job_profile_id: int = Query(...),
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> ResumeResponse:
    row = await service.create_opening_resume(
        conn, current_user["id"], opening_id, source_job_profile_id
    )
    return ResumeResponse(**dict(row))


@router.get(
    "/job-openings/{opening_id}/resume",
    response_model=ResumeResponse,
)
async def get_resume(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> ResumeResponse:
    row = await service.get_opening_resume(conn, current_user["id"], opening_id)
    return ResumeResponse(**dict(row))
