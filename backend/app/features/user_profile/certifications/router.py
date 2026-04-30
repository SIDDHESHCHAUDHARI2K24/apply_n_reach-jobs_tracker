"""Router for certifications CRUD endpoints."""
import asyncpg
from fastapi import APIRouter, Depends, status

from app.features.core.dependencies import DbDep
from app.features.user_profile.dependencies import get_profile_or_404
from app.features.user_profile.certifications import service
from app.features.user_profile.certifications.schemas import CertificationCreate, CertificationResponse, CertificationUpdate

router = APIRouter(prefix="/profile/certifications", tags=["user-profile"])


def _row_to_response(row: asyncpg.Record) -> CertificationResponse:
    """Convert an asyncpg Record to CertificationResponse."""
    return CertificationResponse(**dict(row))


@router.get("", response_model=list[CertificationResponse])
async def list_certifications(
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> list:
    """List all certification entries for the authenticated user's profile."""
    rows = await service.list_certifications(conn, profile["id"])
    return [_row_to_response(row) for row in rows]


@router.get("/{certification_id}", response_model=CertificationResponse)
async def get_certification(
    certification_id: int,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> CertificationResponse:
    """Get a single certification entry by id."""
    row = await service.get_certification(conn, profile["id"], certification_id)
    return _row_to_response(row)


@router.post("", response_model=CertificationResponse, status_code=201)
async def add_certification(
    data: CertificationCreate,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> CertificationResponse:
    """Create a new certification entry."""
    row = await service.add_certification(conn, profile["id"], data)
    return _row_to_response(row)


@router.patch("/{certification_id}", response_model=CertificationResponse)
async def update_certification(
    certification_id: int,
    data: CertificationUpdate,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> CertificationResponse:
    """Partially update an existing certification entry."""
    row = await service.update_certification(conn, profile["id"], certification_id, data)
    return _row_to_response(row)


@router.delete("/{certification_id}", status_code=204)
async def delete_certification(
    certification_id: int,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> None:
    """Delete a certification entry."""
    await service.delete_certification(conn, profile["id"], certification_id)
