"""Router for skills endpoints."""
import asyncpg
from fastapi import APIRouter, Depends

from app.features.core.dependencies import DbDep
from app.features.user_profile.dependencies import get_profile_or_404
from app.features.user_profile.skills import service
from app.features.user_profile.skills.schemas import SkillItemResponse, SkillsUpdate

router = APIRouter(prefix="/profile/skills", tags=["user-profile"])


@router.get("", response_model=list[SkillItemResponse])
async def list_skills(
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> list:
    """List all skill items for the authenticated user's profile."""
    rows = await service.list_skills(conn, profile["id"])
    return [SkillItemResponse(**dict(row)) for row in rows]


@router.get("/{skill_id}", response_model=SkillItemResponse)
async def get_skill(
    skill_id: int,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> SkillItemResponse:
    """Get a single skill item by id."""
    row = await service.get_skill(conn, profile["id"], skill_id)
    return SkillItemResponse(**dict(row))


@router.patch("", response_model=list[SkillItemResponse])
async def replace_skills(
    data: SkillsUpdate,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> list:
    """Replace the full skill set for the authenticated user's profile.

    This is a full replace: all existing skills are deleted and replaced with
    the provided list. Send an empty list to clear all skills.
    """
    rows = await service.replace_skills(conn, profile["id"], data)
    return [SkillItemResponse(**dict(row)) for row in rows]
