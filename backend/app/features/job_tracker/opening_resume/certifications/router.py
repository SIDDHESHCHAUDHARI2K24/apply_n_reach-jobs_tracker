"""Router for job opening resume certifications section endpoints."""
import asyncpg
from fastapi import APIRouter, Depends, Response, status

from app.features.core.dependencies import DbDep
from app.features.auth.utils import get_current_user
from app.features.job_tracker.opening_resume.certifications import service
from app.features.job_tracker.opening_resume.certifications.schemas import (
    CertificationCreate,
    CertificationResponse,
    CertificationUpdate,
)

router = APIRouter(tags=["job-opening-resume"])


@router.get(
    "/job-openings/{opening_id}/resume/certifications",
    response_model=list[CertificationResponse],
)
async def list_certifications(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> list[CertificationResponse]:
    rows = await service.list_entries(conn, current_user["id"], opening_id)
    return [CertificationResponse(**dict(r)) for r in rows]


@router.post(
    "/job-openings/{opening_id}/resume/certifications",
    response_model=CertificationResponse,
    status_code=201,
)
async def create_certification(
    opening_id: int,
    data: CertificationCreate,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> CertificationResponse:
    row = await service.create_entry(conn, current_user["id"], opening_id, data)
    return CertificationResponse(**dict(row))


@router.get(
    "/job-openings/{opening_id}/resume/certifications/{entry_id}",
    response_model=CertificationResponse,
)
async def get_certification(
    opening_id: int,
    entry_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> CertificationResponse:
    row = await service.get_entry(conn, current_user["id"], opening_id, entry_id)
    return CertificationResponse(**dict(row))


@router.patch(
    "/job-openings/{opening_id}/resume/certifications/{entry_id}",
    response_model=CertificationResponse,
)
async def update_certification(
    opening_id: int,
    entry_id: int,
    data: CertificationUpdate,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> CertificationResponse:
    row = await service.update_entry(conn, current_user["id"], opening_id, entry_id, data)
    return CertificationResponse(**dict(row))


@router.delete(
    "/job-openings/{opening_id}/resume/certifications/{entry_id}",
    status_code=204,
)
async def delete_certification(
    opening_id: int,
    entry_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> Response:
    await service.delete_entry(conn, current_user["id"], opening_id, entry_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
