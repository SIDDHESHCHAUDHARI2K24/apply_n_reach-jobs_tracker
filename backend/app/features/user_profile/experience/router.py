"""Router for experience CRUD endpoints."""
import json
import asyncpg
from fastapi import APIRouter, Depends, status

from app.features.core.dependencies import DbDep
from app.features.user_profile.dependencies import get_profile_or_404
from app.features.user_profile.experience import service
from app.features.user_profile.experience.schemas import ExperienceCreate, ExperienceResponse, ExperienceUpdate

# TODO: Register `experience_router` in app/app.py
router = APIRouter(prefix="/profile/experience", tags=["user-profile"])


def _row_to_response(row: asyncpg.Record) -> ExperienceResponse:
    """Convert an asyncpg Record to ExperienceResponse, deserializing JSONB fields."""
    data = dict(row)
    for field in ("work_sample_links", "bullet_points"):
        if isinstance(data[field], str):
            data[field] = json.loads(data[field])
    return ExperienceResponse(**data)


@router.get("", response_model=list[ExperienceResponse])
async def list_experiences(
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> list:
    """List all experience entries for the authenticated user's profile."""
    rows = await service.list_experiences(conn, profile["id"])
    return [_row_to_response(row) for row in rows]


@router.get("/{experience_id}", response_model=ExperienceResponse)
async def get_experience(
    experience_id: int,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> ExperienceResponse:
    """Get a single experience entry by id."""
    row = await service.get_experience(conn, profile["id"], experience_id)
    return _row_to_response(row)


@router.post("", response_model=ExperienceResponse, status_code=201)
async def add_experience(
    data: ExperienceCreate,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> ExperienceResponse:
    """Create a new experience entry."""
    row = await service.add_experience(conn, profile["id"], data)
    return _row_to_response(row)


@router.patch("/{experience_id}", response_model=ExperienceResponse)
async def update_experience(
    experience_id: int,
    data: ExperienceUpdate,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> ExperienceResponse:
    """Partially update an existing experience entry."""
    row = await service.update_experience(conn, profile["id"], experience_id, data)
    return _row_to_response(row)


@router.delete("/{experience_id}", status_code=204)
async def delete_experience(
    experience_id: int,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> None:
    """Delete an experience entry."""
    await service.delete_experience(conn, profile["id"], experience_id)
