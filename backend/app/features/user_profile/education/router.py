"""Router for education CRUD endpoints."""
import json
import asyncpg
from fastapi import APIRouter, Depends, status

from app.features.core.dependencies import DbDep
from app.features.user_profile.dependencies import get_profile_or_404
from app.features.user_profile.education import service
from app.features.user_profile.education.schemas import EducationCreate, EducationResponse

router = APIRouter(prefix="/profile/education", tags=["user-profile"])


def _row_to_response(row: asyncpg.Record) -> EducationResponse:
    """Convert an asyncpg Record to EducationResponse, deserializing JSONB fields."""
    data = dict(row)
    for field in ("bullet_points", "reference_links"):
        if isinstance(data[field], str):
            data[field] = json.loads(data[field])
    return EducationResponse(**data)


@router.get("", response_model=list[EducationResponse])
async def list_educations(
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> list:
    """List all education entries for the authenticated user's profile."""
    rows = await service.list_educations(conn, profile["id"])
    return [_row_to_response(row) for row in rows]


@router.get("/{education_id}", response_model=EducationResponse)
async def get_education(
    education_id: int,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> EducationResponse:
    """Get a single education entry by id."""
    row = await service.get_education(conn, profile["id"], education_id)
    return _row_to_response(row)


@router.post("", response_model=EducationResponse, status_code=201)
async def add_education(
    data: EducationCreate,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> EducationResponse:
    """Create a new education entry."""
    row = await service.add_education(conn, profile["id"], data)
    return _row_to_response(row)


@router.patch("/{education_id}", response_model=EducationResponse)
async def update_education(
    education_id: int,
    data: EducationCreate,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> EducationResponse:
    """Update an existing education entry."""
    row = await service.update_education(conn, profile["id"], education_id, data)
    return _row_to_response(row)


@router.delete("/{education_id}", status_code=204)
async def delete_education(
    education_id: int,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> None:
    """Delete an education entry."""
    await service.delete_education(conn, profile["id"], education_id)
