"""Service functions for the education sub-feature."""
import json
import asyncpg
from fastapi import HTTPException, status

from app.features.core.query_helpers import build_partial_update_query
from app.features.user_profile.education import models
from app.features.user_profile.education.schemas import EducationCreate, EducationUpdate
from app.features.user_profile.education.schemas import _parse_month_year


async def list_educations(conn: asyncpg.Connection, profile_id: int) -> list[asyncpg.Record]:
    """List all education entries for a profile, ordered by start_month_year DESC."""
    await models.ensure_education_schema(conn)
    return await conn.fetch(
        "SELECT id, profile_id, university_name, major, degree_type, "
        "start_month_year, end_month_year, bullet_points, reference_links, "
        "created_at, updated_at FROM educations WHERE profile_id = $1 "
        "ORDER BY start_month_year DESC",
        profile_id,
    )


async def get_education(
    conn: asyncpg.Connection, profile_id: int, education_id: int
) -> asyncpg.Record:
    """Fetch a single education entry, verifying ownership."""
    await models.ensure_education_schema(conn)
    row = await conn.fetchrow(
        "SELECT id, profile_id, university_name, major, degree_type, "
        "start_month_year, end_month_year, bullet_points, reference_links, "
        "created_at, updated_at FROM educations WHERE id = $1 AND profile_id = $2",
        education_id,
        profile_id,
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education entry not found")
    return row


async def add_education(
    conn: asyncpg.Connection, profile_id: int, data: EducationCreate
) -> asyncpg.Record:
    """Create a new education entry for a profile."""
    await models.ensure_education_schema(conn)
    return await conn.fetchrow(
        "INSERT INTO educations (profile_id, university_name, major, degree_type, "
        "start_month_year, end_month_year, bullet_points, reference_links) "
        "VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8::jsonb) "
        "RETURNING id, profile_id, university_name, major, degree_type, "
        "start_month_year, end_month_year, bullet_points, reference_links, "
        "created_at, updated_at",
        profile_id,
        data.university_name,
        data.major,
        data.degree_type,
        data.start_month_year,
        data.end_month_year,
        json.dumps(data.bullet_points),
        json.dumps(data.reference_links),
    )


async def update_education(
    conn: asyncpg.Connection, profile_id: int, education_id: int, data: EducationUpdate
) -> asyncpg.Record:
    """Partially update an existing education entry, verifying ownership."""
    await models.ensure_education_schema(conn)
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Cross-validate dates when only one is provided
    has_start = "start_month_year" in updates
    has_end = "end_month_year" in updates
    if has_start ^ has_end:
        existing = await conn.fetchrow(
            "SELECT start_month_year, end_month_year FROM educations WHERE id=$1 AND profile_id=$2",
            education_id, profile_id
        )
        if existing:
            start = updates.get("start_month_year") or existing["start_month_year"]
            end = updates.get("end_month_year") or existing["end_month_year"]
            if end and start:
                if _parse_month_year(end) < _parse_month_year(start):
                    raise HTTPException(status_code=422, detail="end_month_year must be >= start_month_year")

    query, params = build_partial_update_query(
        "educations",
        {"id": education_id, "profile_id": profile_id},
        updates,
        jsonb_fields={"bullet_points", "reference_links"}
    )
    row = await conn.fetchrow(query, *params)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education entry not found")
    return row


async def delete_education(
    conn: asyncpg.Connection, profile_id: int, education_id: int
) -> None:
    """Delete an education entry, verifying ownership."""
    await models.ensure_education_schema(conn)
    result = await conn.execute(
        "DELETE FROM educations WHERE id = $1 AND profile_id = $2",
        education_id,
        profile_id,
    )
    affected = int(result.split()[-1])
    if affected == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education entry not found")
