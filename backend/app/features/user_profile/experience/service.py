"""Service functions for the experience sub-feature."""
import json
import asyncpg
from fastapi import HTTPException, status

from app.features.core.query_helpers import build_partial_update_query
from app.features.user_profile.experience import models
from app.features.user_profile.experience.schemas import ExperienceCreate, ExperienceUpdate
from app.features.user_profile.experience.schemas import _parse_month_year


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
    conn: asyncpg.Connection, profile_id: int, experience_id: int, data: ExperienceUpdate
) -> asyncpg.Record:
    """Partially update an existing experience entry, verifying ownership."""
    await models.ensure_experience_schema(conn)
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Cross-validate dates when only one is provided
    has_start = "start_month_year" in updates
    has_end = "end_month_year" in updates
    if has_start ^ has_end:
        existing = await conn.fetchrow(
            "SELECT start_month_year, end_month_year FROM experiences WHERE id=$1 AND profile_id=$2",
            experience_id, profile_id
        )
        if existing:
            start = updates.get("start_month_year") or existing["start_month_year"]
            end = updates.get("end_month_year") or existing["end_month_year"]
            if end and start:
                if _parse_month_year(end) < _parse_month_year(start):
                    raise HTTPException(status_code=422, detail="end_month_year must be >= start_month_year")

    query, params = build_partial_update_query(
        "experiences",
        {"id": experience_id, "profile_id": profile_id},
        updates,
        jsonb_fields={"work_sample_links", "bullet_points"}
    )
    row = await conn.fetchrow(query, *params)
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
