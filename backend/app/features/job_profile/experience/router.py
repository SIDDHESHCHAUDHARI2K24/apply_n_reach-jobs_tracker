"""Router for job profile experience CRUD and import endpoints."""
import json
import asyncpg
from fastapi import APIRouter, Depends, status

from app.features.core.dependencies import DbDep
from app.features.auth.utils import get_current_user
from app.features.job_profile.dependencies import get_job_profile_or_404
from app.features.job_profile.experience import service
from app.features.job_profile.experience.schemas import (
    JPExperienceCreate,
    JPExperienceResponse,
    JPExperienceUpdate,
)
from app.features.job_profile.import_schemas import ImportRequest, ImportResult

router = APIRouter(
    prefix="/job-profiles/{job_profile_id}/experience",
    tags=["job-profile"],
)


def _row_to_response(row: asyncpg.Record) -> JPExperienceResponse:
    """Convert an asyncpg Record to JPExperienceResponse, deserializing JSONB fields."""
    data = dict(row)
    for field in ("work_sample_links", "bullet_points"):
        if isinstance(data[field], str):
            data[field] = json.loads(data[field])
    return JPExperienceResponse(**data)


@router.get("", response_model=list[JPExperienceResponse])
async def list_experiences(
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> list:
    """List all experience entries for the job profile."""
    rows = await service.list_experiences(conn, job_profile["id"])
    return [_row_to_response(row) for row in rows]


@router.get("/{experience_id}", response_model=JPExperienceResponse)
async def get_experience(
    experience_id: int,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> JPExperienceResponse:
    """Get a single experience entry by id."""
    row = await service.get_experience(conn, job_profile["id"], experience_id)
    return _row_to_response(row)


@router.post("", response_model=JPExperienceResponse, status_code=201)
async def add_experience(
    data: JPExperienceCreate,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> JPExperienceResponse:
    """Create a new experience entry for the job profile."""
    row = await service.add_experience(conn, job_profile["id"], data)
    return _row_to_response(row)


@router.patch("/{experience_id}", response_model=JPExperienceResponse)
async def update_experience(
    experience_id: int,
    data: JPExperienceUpdate,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> JPExperienceResponse:
    """Partially update an existing experience entry."""
    row = await service.update_experience(conn, job_profile["id"], experience_id, data)
    return _row_to_response(row)


@router.delete("/{experience_id}", status_code=204)
async def delete_experience(
    experience_id: int,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> None:
    """Delete an experience entry."""
    await service.delete_experience(conn, job_profile["id"], experience_id)


@router.post("/import", response_model=ImportResult)
async def import_experiences(
    data: ImportRequest,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    current_user: asyncpg.Record = Depends(get_current_user),
    conn: asyncpg.Connection = DbDep,
) -> ImportResult:
    """Import experience entries from the user's master profile into this job profile."""
    return await service.import_experiences_from_profile(
        conn,
        job_profile["id"],
        current_user["id"],
        data.source_ids,
    )
