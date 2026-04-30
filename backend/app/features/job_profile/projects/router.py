"""Router for job profile projects endpoints."""
import json
import asyncpg
from fastapi import APIRouter, Depends, Response, status

from app.features.core.dependencies import DbDep
from app.features.auth.utils import get_current_user
from app.features.job_profile.dependencies import get_job_profile_or_404
from app.features.job_profile.projects import service
from app.features.job_profile.projects.schemas import (
    JPProjectCreate,
    JPProjectResponse,
    JPProjectUpdate,
)
from app.features.job_profile.import_schemas import ImportRequest, ImportResult

router = APIRouter(prefix="/job-profiles/{job_profile_id}/projects", tags=["job-profile"])


def _row_to_response(row: asyncpg.Record) -> JPProjectResponse:
    d = dict(row)
    if isinstance(d.get("reference_links"), str):
        d["reference_links"] = json.loads(d["reference_links"])
    if isinstance(d.get("technologies"), str):
        d["technologies"] = json.loads(d["technologies"])
    return JPProjectResponse(**d)


@router.get("", response_model=list[JPProjectResponse])
async def list_projects(
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> list[JPProjectResponse]:
    rows = await service.list_projects(conn, job_profile["id"])
    return [_row_to_response(r) for r in rows]


@router.get("/{project_id}", response_model=JPProjectResponse)
async def get_project(
    project_id: int,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> JPProjectResponse:
    row = await service.get_project(conn, job_profile["id"], project_id)
    return _row_to_response(row)


@router.post("", response_model=JPProjectResponse, status_code=201)
async def add_project(
    data: JPProjectCreate,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> JPProjectResponse:
    row = await service.add_project(conn, job_profile["id"], data)
    return _row_to_response(row)


@router.patch("/{project_id}", response_model=JPProjectResponse)
async def update_project(
    project_id: int,
    data: JPProjectUpdate,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> JPProjectResponse:
    row = await service.update_project(conn, job_profile["id"], project_id, data)
    return _row_to_response(row)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> Response:
    await service.delete_project(conn, job_profile["id"], project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/import", response_model=ImportResult, status_code=200)
async def import_projects(
    data: ImportRequest,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    current_user: asyncpg.Record = Depends(get_current_user),
    conn: asyncpg.Connection = DbDep,
) -> ImportResult:
    return await service.import_projects_from_profile(
        conn, job_profile["id"], current_user["id"], data.source_ids
    )
