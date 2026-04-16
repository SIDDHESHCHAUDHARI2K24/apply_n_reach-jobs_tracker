"""Router for job opening resume education section endpoints."""
import asyncpg
from fastapi import APIRouter, Depends, Response, status

from app.features.core.dependencies import DbDep
from app.features.auth.utils import get_current_user
from app.features.job_tracker.opening_resume.education import service
from app.features.job_tracker.opening_resume.education.schemas import (
    EducationCreate,
    EducationResponse,
    EducationUpdate,
)

router = APIRouter(tags=["job-opening-resume"])


@router.get(
    "/job-openings/{opening_id}/resume/education",
    response_model=list[EducationResponse],
)
async def list_education(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> list[EducationResponse]:
    rows = await service.list_entries(conn, current_user["id"], opening_id)
    return [EducationResponse(**dict(r)) for r in rows]


@router.post(
    "/job-openings/{opening_id}/resume/education",
    response_model=EducationResponse,
    status_code=201,
)
async def create_education(
    opening_id: int,
    data: EducationCreate,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> EducationResponse:
    row = await service.create_entry(conn, current_user["id"], opening_id, data)
    return EducationResponse(**dict(row))


@router.get(
    "/job-openings/{opening_id}/resume/education/{entry_id}",
    response_model=EducationResponse,
)
async def get_education(
    opening_id: int,
    entry_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> EducationResponse:
    row = await service.get_entry(conn, current_user["id"], opening_id, entry_id)
    return EducationResponse(**dict(row))


@router.patch(
    "/job-openings/{opening_id}/resume/education/{entry_id}",
    response_model=EducationResponse,
)
async def update_education(
    opening_id: int,
    entry_id: int,
    data: EducationUpdate,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> EducationResponse:
    row = await service.update_entry(conn, current_user["id"], opening_id, entry_id, data)
    return EducationResponse(**dict(row))


@router.delete(
    "/job-openings/{opening_id}/resume/education/{entry_id}",
    status_code=204,
)
async def delete_education(
    opening_id: int,
    entry_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> Response:
    await service.delete_entry(conn, current_user["id"], opening_id, entry_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
