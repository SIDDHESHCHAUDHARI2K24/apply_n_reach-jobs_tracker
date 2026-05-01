"""Router for job_profile status transition endpoints."""
import asyncpg
from fastapi import APIRouter, Depends

from app.features.core.dependencies import DbDep
from app.features.job_profile.core.schemas import JobProfileResponse
from app.features.job_profile.dependencies import get_job_profile_or_404
from app.features.job_profile.status import service
from app.features.job_profile.status.schemas import JobProfileStatus

router = APIRouter(prefix="/job-profiles/{job_profile_id}/status", tags=["job-profile"])


@router.post("/activate", response_model=JobProfileResponse)
async def activate_job_profile(
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> JobProfileResponse:
    """Activate a draft or archived job profile."""
    row = await service.transition_job_profile_status(conn, job_profile, JobProfileStatus.Active)
    return JobProfileResponse(**dict(row))


@router.post("/archive", response_model=JobProfileResponse)
async def archive_job_profile(
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> JobProfileResponse:
    """Archive an active or draft job profile."""
    row = await service.transition_job_profile_status(conn, job_profile, JobProfileStatus.Archived)
    return JobProfileResponse(**dict(row))

