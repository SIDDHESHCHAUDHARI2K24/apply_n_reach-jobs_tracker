"""Router for job opening resume skills section endpoints."""
import asyncpg
from fastapi import APIRouter, Depends, Response, status

from app.features.core.dependencies import DbDep
from app.features.auth.utils import get_current_user
from app.features.job_tracker.opening_resume.skills import service
from app.features.job_tracker.opening_resume.skills.schemas import (
    SkillCreate,
    SkillResponse,
    SkillUpdate,
)

router = APIRouter(tags=["job-opening-resume"])


@router.get(
    "/job-openings/{opening_id}/resume/skills",
    response_model=list[SkillResponse],
)
async def list_skills(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> list[SkillResponse]:
    rows = await service.list_entries(conn, current_user["id"], opening_id)
    return [SkillResponse(**dict(r)) for r in rows]


@router.post(
    "/job-openings/{opening_id}/resume/skills",
    response_model=SkillResponse,
    status_code=201,
)
async def create_skill(
    opening_id: int,
    data: SkillCreate,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> SkillResponse:
    row = await service.create_entry(conn, current_user["id"], opening_id, data)
    return SkillResponse(**dict(row))


@router.get(
    "/job-openings/{opening_id}/resume/skills/{entry_id}",
    response_model=SkillResponse,
)
async def get_skill(
    opening_id: int,
    entry_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> SkillResponse:
    row = await service.get_entry(conn, current_user["id"], opening_id, entry_id)
    return SkillResponse(**dict(row))


@router.patch(
    "/job-openings/{opening_id}/resume/skills/{entry_id}",
    response_model=SkillResponse,
)
async def update_skill(
    opening_id: int,
    entry_id: int,
    data: SkillUpdate,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> SkillResponse:
    row = await service.update_entry(conn, current_user["id"], opening_id, entry_id, data)
    return SkillResponse(**dict(row))


@router.delete(
    "/job-openings/{opening_id}/resume/skills/{entry_id}",
    status_code=204,
)
async def delete_skill(
    opening_id: int,
    entry_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> Response:
    await service.delete_entry(conn, current_user["id"], opening_id, entry_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
