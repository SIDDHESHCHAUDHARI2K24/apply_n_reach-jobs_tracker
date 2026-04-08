"""Router for job profile skills replace-all and import endpoints."""
import asyncpg
from fastapi import APIRouter, Depends

from app.features.core.dependencies import DbDep
from app.features.auth.utils import get_current_user
from app.features.job_profile.dependencies import get_job_profile_or_404
from app.features.job_profile.skills import service
from app.features.job_profile.skills.schemas import (
    JPSkillItemResponse,
    JPSkillsUpdate,
)
from app.features.job_profile.import_schemas import ImportRequest, ImportResult

router = APIRouter(
    prefix="/job-profiles/{job_profile_id}/skills",
    tags=["job-profile"],
)


@router.get("", response_model=list[JPSkillItemResponse])
async def list_skills(
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> list:
    """List all skill items for the job profile."""
    rows = await service.list_skills(conn, job_profile["id"])
    return [JPSkillItemResponse(**dict(r)) for r in rows]


@router.get("/{skill_id}", response_model=JPSkillItemResponse)
async def get_skill(
    skill_id: int,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> JPSkillItemResponse:
    """Get a single skill item by id."""
    row = await service.get_skill(conn, job_profile["id"], skill_id)
    return JPSkillItemResponse(**dict(row))


@router.patch("", response_model=list[JPSkillItemResponse])
async def replace_skills(
    data: JPSkillsUpdate,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> list:
    """Replace all skill items for the job profile (delete-all + insert)."""
    rows = await service.replace_skills(conn, job_profile["id"], data.skills)
    return [JPSkillItemResponse(**dict(r)) for r in rows]


@router.post("/import", response_model=ImportResult, status_code=200)
async def import_skills(
    data: ImportRequest,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    current_user: asyncpg.Record = Depends(get_current_user),
    conn: asyncpg.Connection = DbDep,
) -> ImportResult:
    """Additively import skill items from the user's master profile."""
    return await service.import_skills_from_profile(
        conn,
        job_profile["id"],
        current_user["id"],
        data.source_ids,
    )
