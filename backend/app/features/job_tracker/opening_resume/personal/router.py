"""Router for job opening resume personal section endpoints."""
import asyncpg
from fastapi import APIRouter, Depends

from app.features.core.dependencies import DbDep
from app.features.auth.utils import get_current_user
from app.features.job_tracker.opening_resume.personal import service
from app.features.job_tracker.opening_resume.personal.schemas import (
    PersonalResponse,
    PersonalUpdate,
)

router = APIRouter(tags=["job-opening-resume"])


@router.get(
    "/job-openings/{opening_id}/resume/personal",
    response_model=PersonalResponse,
)
async def get_personal(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> PersonalResponse:
    row = await service.get_personal(conn, current_user["id"], opening_id)
    return PersonalResponse(**dict(row))


@router.put(
    "/job-openings/{opening_id}/resume/personal",
    response_model=PersonalResponse,
)
async def upsert_personal(
    opening_id: int,
    data: PersonalUpdate,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> PersonalResponse:
    row = await service.upsert_personal(conn, current_user["id"], opening_id, data)
    return PersonalResponse(**dict(row))
