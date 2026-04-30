"""Service functions for the job_profile experience sub-feature."""
import json
import asyncpg
from fastapi import HTTPException, status

from app.features.core.query_helpers import build_partial_update_query
from app.features.job_profile.experience import models
from app.features.job_profile.experience.schemas import (
    JPExperienceCreate,
    JPExperienceUpdate,
    _parse_month_year,
)
from app.features.job_profile.import_helpers import (
    validate_source_ownership,
    get_already_imported,
)
from app.features.job_profile.import_schemas import ImportResult


async def list_experiences(
    conn: asyncpg.Connection, job_profile_id: int
) -> list[asyncpg.Record]:
    """List all experience entries for a job profile, ordered by start_month_year DESC."""
    await models.ensure_jp_experience_schema(conn)
    return await conn.fetch(
        "SELECT * FROM job_profile_experiences WHERE job_profile_id = $1 "
        "ORDER BY start_month_year DESC",
        job_profile_id,
    )


async def get_experience(
    conn: asyncpg.Connection, job_profile_id: int, experience_id: int
) -> asyncpg.Record:
    """Fetch a single experience entry, verifying ownership via job_profile_id."""
    await models.ensure_jp_experience_schema(conn)
    row = await conn.fetchrow(
        "SELECT * FROM job_profile_experiences WHERE id = $1 AND job_profile_id = $2",
        experience_id,
        job_profile_id,
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience entry not found",
        )
    return row


async def add_experience(
    conn: asyncpg.Connection, job_profile_id: int, data: JPExperienceCreate
) -> asyncpg.Record:
    """Create a new experience entry for a job profile."""
    await models.ensure_jp_experience_schema(conn)
    row = await conn.fetchrow(
        "INSERT INTO job_profile_experiences "
        "(job_profile_id, source_experience_id, role_title, company_name, location, "
        "start_month_year, end_month_year, context, work_sample_links, bullet_points) "
        "VALUES ($1, NULL, $2, $3, $4, $5, $6, $7, $8::jsonb, $9::jsonb) "
        "RETURNING *",
        job_profile_id,
        data.role_title,
        data.company_name,
        data.location,
        data.start_month_year,
        data.end_month_year,
        data.context,
        json.dumps(data.work_sample_links),
        json.dumps(data.bullet_points),
    )
    return row


async def update_experience(
    conn: asyncpg.Connection,
    job_profile_id: int,
    experience_id: int,
    data: JPExperienceUpdate,
) -> asyncpg.Record:
    """Partially update an existing experience entry, verifying ownership."""
    await models.ensure_jp_experience_schema(conn)
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Cross-validate dates when only one is provided
    has_start = "start_month_year" in updates
    has_end = "end_month_year" in updates
    if has_start ^ has_end:
        existing = await conn.fetchrow(
            "SELECT start_month_year, end_month_year FROM job_profile_experiences "
            "WHERE id = $1 AND job_profile_id = $2",
            experience_id,
            job_profile_id,
        )
        if existing:
            start = updates.get("start_month_year") or existing["start_month_year"]
            end = updates.get("end_month_year") or existing["end_month_year"]
            if end and start:
                if _parse_month_year(end) < _parse_month_year(start):
                    raise HTTPException(
                        status_code=422,
                        detail="end_month_year must be >= start_month_year",
                    )

    query, params = build_partial_update_query(
        "job_profile_experiences",
        {"id": experience_id, "job_profile_id": job_profile_id},
        updates,
        jsonb_fields={"work_sample_links", "bullet_points"},
    )
    row = await conn.fetchrow(query, *params)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience entry not found",
        )
    return row


async def delete_experience(
    conn: asyncpg.Connection, job_profile_id: int, experience_id: int
) -> None:
    """Delete an experience entry, verifying ownership."""
    await models.ensure_jp_experience_schema(conn)
    result = await conn.execute(
        "DELETE FROM job_profile_experiences WHERE id = $1 AND job_profile_id = $2",
        experience_id,
        job_profile_id,
    )
    affected = int(result.split()[-1])
    if affected == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience entry not found",
        )


async def import_experiences_from_profile(
    conn: asyncpg.Connection,
    job_profile_id: int,
    user_id: int,
    source_ids: list[int],
) -> ImportResult:
    """Import experience entries from the user's master profile into a job profile."""
    await models.ensure_jp_experience_schema(conn)

    # 1. Validate source ownership
    valid_ids, not_found_ids = await validate_source_ownership(
        conn, "experiences", source_ids, user_id
    )

    if not valid_ids:
        return ImportResult(imported=[], skipped=[], not_found=not_found_ids)

    # 2. Detect already-imported IDs
    already_imported = await get_already_imported(
        conn,
        "job_profile_experiences",
        job_profile_id,
        "source_experience_id",
        valid_ids,
    )
    already_imported_set = set(already_imported)

    to_import = [sid for sid in valid_ids if sid not in already_imported_set]
    skipped_ids = [sid for sid in valid_ids if sid in already_imported_set]

    if not to_import:
        return ImportResult(imported=[], skipped=skipped_ids, not_found=not_found_ids)

    # 3. Fetch source rows
    source_rows = await conn.fetch(
        "SELECT * FROM experiences WHERE id = ANY($1)",
        to_import,
    )

    # 4. Insert each row within a transaction
    imported_ids = []
    async with conn.transaction():
        for row in source_rows:
            # asyncpg returns JSONB as Python list from SELECT — use json.dumps() when inserting
            work_sample_links = row["work_sample_links"]
            bullet_points = row["bullet_points"]
            if not isinstance(work_sample_links, str):
                work_sample_links = json.dumps(work_sample_links)
            if not isinstance(bullet_points, str):
                bullet_points = json.dumps(bullet_points)

            inserted = await conn.fetchrow(
                "INSERT INTO job_profile_experiences "
                "(job_profile_id, source_experience_id, role_title, company_name, location, "
                "start_month_year, end_month_year, context, work_sample_links, bullet_points) "
                "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb, $10::jsonb) "
                "RETURNING id",
                job_profile_id,
                row["id"],
                row["role_title"],
                row["company_name"],
                row["location"],
                row["start_month_year"],
                row["end_month_year"],
                row["context"],
                work_sample_links,
                bullet_points,
            )
            imported_ids.append(row["id"])

    # 5. Return ImportResult
    return ImportResult(
        imported=imported_ids,
        skipped=skipped_ids,
        not_found=not_found_ids,
    )
