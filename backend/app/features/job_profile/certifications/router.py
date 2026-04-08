"""Router for job profile certifications CRUD endpoints."""
import asyncpg
from fastapi import APIRouter, Depends, status

from app.features.core.dependencies import DbDep
from app.features.auth.utils import get_current_user
from app.features.job_profile.dependencies import get_job_profile_or_404
from app.features.job_profile.certifications import service
from app.features.job_profile.certifications.schemas import (
    JPCertificationCreate,
    JPCertificationUpdate,
    JPCertificationResponse,
)
from app.features.job_profile.import_schemas import ImportRequest, ImportResult

router = APIRouter(prefix="/job-profiles/{job_profile_id}/certifications", tags=["job-profile"])


def _row_to_response(row: asyncpg.Record) -> JPCertificationResponse:
    """Convert an asyncpg Record to JPCertificationResponse."""
    return JPCertificationResponse(**dict(row))


@router.get("", response_model=list[JPCertificationResponse])
async def list_certifications(
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> list:
    """List all certification entries for a job profile."""
    rows = await service.list_certifications(conn, job_profile["id"])
    return [_row_to_response(row) for row in rows]


@router.get("/{cert_id}", response_model=JPCertificationResponse)
async def get_certification(
    cert_id: int,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> JPCertificationResponse:
    """Get a single certification entry by id."""
    row = await service.get_certification(conn, job_profile["id"], cert_id)
    return _row_to_response(row)


@router.post("", response_model=JPCertificationResponse, status_code=201)
async def add_certification(
    data: JPCertificationCreate,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> JPCertificationResponse:
    """Create a new certification entry for a job profile."""
    row = await service.add_certification(conn, job_profile["id"], data)
    return _row_to_response(row)


@router.patch("/{cert_id}", response_model=JPCertificationResponse)
async def update_certification(
    cert_id: int,
    data: JPCertificationUpdate,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> JPCertificationResponse:
    """Partially update an existing certification entry."""
    row = await service.update_certification(conn, job_profile["id"], cert_id, data)
    return _row_to_response(row)


@router.delete("/{cert_id}", status_code=204)
async def delete_certification(
    cert_id: int,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> None:
    """Delete a certification entry."""
    await service.delete_certification(conn, job_profile["id"], cert_id)


@router.post("/import", response_model=ImportResult)
async def import_certifications(
    data: ImportRequest,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    current_user: asyncpg.Record = Depends(get_current_user),
    conn: asyncpg.Connection = DbDep,
) -> ImportResult:
    """Import certification entries from the user's master profile."""
    return await service.import_certifications_from_profile(
        conn, job_profile["id"], current_user["id"], data.source_ids
    )
