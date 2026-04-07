"""Router for job profile CRUD endpoints."""
import asyncpg
from fastapi import APIRouter, Depends, Query, status

from app.features.core.base_model import PaginatedResponse
from app.features.core.dependencies import DbDep
from app.features.auth.utils import get_current_user
from app.features.job_profile.core import service
from app.features.job_profile.core.schemas import (
    JobProfileCreate,
    JobProfileListParams,
    JobProfileResponse,
    JobProfileUpdate,
)

router = APIRouter(prefix="/job-profiles", tags=["job-profile"])


@router.post("", response_model=JobProfileResponse, status_code=201)
async def create_job_profile(
    data: JobProfileCreate,
    current_user: asyncpg.Record = Depends(get_current_user),
    conn: asyncpg.Connection = DbDep,
) -> JobProfileResponse:
    """Create a new job profile."""
    row = await service.create_job_profile(conn, current_user["id"], data)
    return JobProfileResponse(**dict(row))


@router.get("", response_model=PaginatedResponse[JobProfileResponse])
async def list_job_profiles(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: str = Query(None, alias="status"),
    current_user: asyncpg.Record = Depends(get_current_user),
    conn: asyncpg.Connection = DbDep,
) -> PaginatedResponse[JobProfileResponse]:
    """List job profiles for the authenticated user."""
    params = JobProfileListParams(limit=limit, offset=offset, status=status_filter)
    rows, total = await service.list_job_profiles(conn, current_user["id"], params)
    return PaginatedResponse(
        items=[JobProfileResponse(**dict(row)) for row in rows],
        total=total,
        limit=params.limit,
        offset=params.offset,
    )


@router.get("/{job_profile_id}", response_model=JobProfileResponse)
async def get_job_profile(
    job_profile_id: int,
    current_user: asyncpg.Record = Depends(get_current_user),
    conn: asyncpg.Connection = DbDep,
) -> JobProfileResponse:
    """Get a single job profile by id."""
    row = await service.get_job_profile(conn, current_user["id"], job_profile_id)
    return JobProfileResponse(**dict(row))


@router.patch("/{job_profile_id}", response_model=JobProfileResponse)
async def update_job_profile(
    job_profile_id: int,
    data: JobProfileUpdate,
    current_user: asyncpg.Record = Depends(get_current_user),
    conn: asyncpg.Connection = DbDep,
) -> JobProfileResponse:
    """Partially update a job profile."""
    row = await service.update_job_profile(conn, current_user["id"], job_profile_id, data)
    return JobProfileResponse(**dict(row))


@router.delete("/{job_profile_id}", status_code=204)
async def delete_job_profile(
    job_profile_id: int,
    current_user: asyncpg.Record = Depends(get_current_user),
    conn: asyncpg.Connection = DbDep,
) -> None:
    """Delete a job profile."""
    await service.delete_job_profile(conn, current_user["id"], job_profile_id)
