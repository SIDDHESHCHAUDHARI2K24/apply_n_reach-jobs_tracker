"""Router for job opening resume projects section endpoints."""
import asyncpg
from fastapi import APIRouter, Depends, Response, status

from app.features.core.dependencies import DbDep
from app.features.auth.utils import get_current_user
from app.features.job_tracker.opening_resume.projects import service
from app.features.job_tracker.opening_resume.projects.schemas import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)

router = APIRouter(tags=["job-opening-resume"])


@router.get(
    "/job-openings/{opening_id}/resume/projects",
    response_model=list[ProjectResponse],
)
async def list_projects(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> list[ProjectResponse]:
    rows = await service.list_entries(conn, current_user["id"], opening_id)
    return [ProjectResponse(**service._parse_project_row(r)) for r in rows]


@router.post(
    "/job-openings/{opening_id}/resume/projects",
    response_model=ProjectResponse,
    status_code=201,
)
async def create_project(
    opening_id: int,
    data: ProjectCreate,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> ProjectResponse:
    row = await service.create_entry(conn, current_user["id"], opening_id, data)
    return ProjectResponse(**service._parse_project_row(row))


@router.get(
    "/job-openings/{opening_id}/resume/projects/{entry_id}",
    response_model=ProjectResponse,
)
async def get_project(
    opening_id: int,
    entry_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> ProjectResponse:
    row = await service.get_entry(conn, current_user["id"], opening_id, entry_id)
    return ProjectResponse(**service._parse_project_row(row))


@router.patch(
    "/job-openings/{opening_id}/resume/projects/{entry_id}",
    response_model=ProjectResponse,
)
async def update_project(
    opening_id: int,
    entry_id: int,
    data: ProjectUpdate,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> ProjectResponse:
    row = await service.update_entry(conn, current_user["id"], opening_id, entry_id, data)
    return ProjectResponse(**service._parse_project_row(row))


@router.delete(
    "/job-openings/{opening_id}/resume/projects/{entry_id}",
    status_code=204,
)
async def delete_project(
    opening_id: int,
    entry_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> Response:
    await service.delete_entry(conn, current_user["id"], opening_id, entry_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
