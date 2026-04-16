"""Router for job opening resume experience section endpoints."""
import asyncpg
from fastapi import APIRouter, Depends, Response, status

from app.features.core.dependencies import DbDep
from app.features.auth.utils import get_current_user
from app.features.job_tracker.opening_resume.experience import service
from app.features.job_tracker.opening_resume.experience.schemas import (
    ExperienceCreate,
    ExperienceResponse,
    ExperienceUpdate,
)

router = APIRouter(tags=["job-opening-resume"])


@router.get(
    "/job-openings/{opening_id}/resume/experience",
    response_model=list[ExperienceResponse],
)
async def list_experience(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> list[ExperienceResponse]:
    rows = await service.list_entries(conn, current_user["id"], opening_id)
    return [ExperienceResponse(**dict(r)) for r in rows]


@router.post(
    "/job-openings/{opening_id}/resume/experience",
    response_model=ExperienceResponse,
    status_code=201,
)
async def create_experience(
    opening_id: int,
    data: ExperienceCreate,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> ExperienceResponse:
    row = await service.create_entry(conn, current_user["id"], opening_id, data)
    return ExperienceResponse(**dict(row))


@router.get(
    "/job-openings/{opening_id}/resume/experience/{entry_id}",
    response_model=ExperienceResponse,
)
async def get_experience(
    opening_id: int,
    entry_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> ExperienceResponse:
    row = await service.get_entry(conn, current_user["id"], opening_id, entry_id)
    return ExperienceResponse(**dict(row))


@router.patch(
    "/job-openings/{opening_id}/resume/experience/{entry_id}",
    response_model=ExperienceResponse,
)
async def update_experience(
    opening_id: int,
    entry_id: int,
    data: ExperienceUpdate,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> ExperienceResponse:
    row = await service.update_entry(conn, current_user["id"], opening_id, entry_id, data)
    return ExperienceResponse(**dict(row))


@router.delete(
    "/job-openings/{opening_id}/resume/experience/{entry_id}",
    status_code=204,
)
async def delete_experience(
    opening_id: int,
    entry_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> Response:
    await service.delete_entry(conn, current_user["id"], opening_id, entry_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
