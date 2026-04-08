"""Router for job profile education endpoints."""
import json
import asyncpg
from fastapi import APIRouter, Depends, Response, status

from app.features.core.dependencies import DbDep
from app.features.auth.utils import get_current_user
from app.features.job_profile.dependencies import get_job_profile_or_404
from app.features.job_profile.education import service
from app.features.job_profile.education.schemas import (
    JPEducationCreate,
    JPEducationResponse,
    JPEducationUpdate,
)
from app.features.job_profile.import_schemas import ImportRequest, ImportResult

router = APIRouter(prefix="/job-profiles/{job_profile_id}/education", tags=["job-profile"])


def _row_to_response(row: asyncpg.Record) -> JPEducationResponse:
    """Deserialize JSONB fields and return the response schema."""
    d = dict(row)
    if isinstance(d.get("bullet_points"), str):
        d["bullet_points"] = json.loads(d["bullet_points"])
    if isinstance(d.get("reference_links"), str):
        d["reference_links"] = json.loads(d["reference_links"])
    return JPEducationResponse(**d)


@router.get("", response_model=list[JPEducationResponse])
async def list_educations(
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> list[JPEducationResponse]:
    rows = await service.list_educations(conn, job_profile["id"])
    return [_row_to_response(r) for r in rows]


@router.get("/{education_id}", response_model=JPEducationResponse)
async def get_education(
    education_id: int,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> JPEducationResponse:
    row = await service.get_education(conn, job_profile["id"], education_id)
    return _row_to_response(row)


@router.post("", response_model=JPEducationResponse, status_code=201)
async def add_education(
    data: JPEducationCreate,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> JPEducationResponse:
    row = await service.add_education(conn, job_profile["id"], data)
    return _row_to_response(row)


@router.patch("/{education_id}", response_model=JPEducationResponse)
async def update_education(
    education_id: int,
    data: JPEducationUpdate,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> JPEducationResponse:
    row = await service.update_education(conn, job_profile["id"], education_id, data)
    return _row_to_response(row)


@router.delete("/{education_id}", status_code=204)
async def delete_education(
    education_id: int,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> Response:
    await service.delete_education(conn, job_profile["id"], education_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/import", response_model=ImportResult, status_code=200)
async def import_educations(
    data: ImportRequest,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    current_user: asyncpg.Record = Depends(get_current_user),
    conn: asyncpg.Connection = DbDep,
) -> ImportResult:
    return await service.import_educations_from_profile(
        conn, job_profile["id"], current_user["id"], data.source_ids
    )
