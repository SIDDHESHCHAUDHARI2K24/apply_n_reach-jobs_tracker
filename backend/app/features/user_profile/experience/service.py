"""Service functions for the experience sub-feature."""
import json
import asyncpg
from fastapi import HTTPException, status

from app.features.user_profile.experience import models
from app.features.user_profile.experience.schemas import ExperienceCreate


async def list_experiences(conn: asyncpg.Connection, profile_id: int) -> list[asyncpg.Record]:
    """List all experience entries for a profile, ordered by start_month_year DESC."""
    await models.ensure_experience_schema(conn)
    return await conn.fetch(
        "SELECT id, profile_id, role_title, company_name, "
        "start_month_year, end_month_year, context, work_sample_links, bullet_points, "
        "created_at, updated_at FROM experiences WHERE profile_id = $1 "
        "ORDER BY start_month_year DESC",
        profile_id,
    )


async def get_experience(
    conn: asyncpg.Connection, profile_id: int, experience_id: int
) -> asyncpg.Record:
    """Fetch a single experience entry, verifying ownership."""
    await models.ensure_experience_schema(conn)
    row = await conn.fetchrow(
        "SELECT id, profile_id, role_title, company_name, "
        "start_month_year, end_month_year, context, work_sample_links, bullet_points, "
        "created_at, updated_at FROM experiences WHERE id = $1 AND profile_id = $2",
        experience_id,
        profile_id,
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience entry not found")
    return row


async def add_experience(
    conn: asyncpg.Connection, profile_id: int, data: ExperienceCreate
) -> asyncpg.Record:
    """Create a new experience entry for a profile."""
    await models.ensure_experience_schema(conn)
    return await conn.fetchrow(
        "INSERT INTO experiences (profile_id, role_title, company_name, "
        "start_month_year, end_month_year, context, work_sample_links, bullet_points) "
        "VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8::jsonb) "
        "RETURNING id, profile_id, role_title, company_name, "
        "start_month_year, end_month_year, context, work_sample_links, bullet_points, "
        "created_at, updated_at",
        profile_id,
        data.role_title,
        data.company_name,
        data.start_month_year,
        data.end_month_year,
        data.context,
        json.dumps(data.work_sample_links),
        json.dumps(data.bullet_points),
    )


async def update_experience(
    conn: asyncpg.Connection, profile_id: int, experience_id: int, data: ExperienceCreate
) -> asyncpg.Record:
    """Update an existing experience entry, verifying ownership."""
    await models.ensure_experience_schema(conn)
    row = await conn.fetchrow(
        "UPDATE experiences SET role_title=$1, company_name=$2, "
        "start_month_year=$3, end_month_year=$4, context=$5, "
        "work_sample_links=$6::jsonb, bullet_points=$7::jsonb, updated_at=NOW() "
        "WHERE id=$8 AND profile_id=$9 "
        "RETURNING id, profile_id, role_title, company_name, "
        "start_month_year, end_month_year, context, work_sample_links, bullet_points, "
        "created_at, updated_at",
        data.role_title,
        data.company_name,
        data.start_month_year,
        data.end_month_year,
        data.context,
        json.dumps(data.work_sample_links),
        json.dumps(data.bullet_points),
        experience_id,
        profile_id,
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience entry not found")
    return row


async def delete_experience(
    conn: asyncpg.Connection, profile_id: int, experience_id: int
) -> None:
    """Delete an experience entry, verifying ownership."""
    await models.ensure_experience_schema(conn)
    result = await conn.execute(
        "DELETE FROM experiences WHERE id = $1 AND profile_id = $2",
        experience_id,
        profile_id,
    )
    affected = int(result.split()[-1])
    if affected == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience entry not found")
