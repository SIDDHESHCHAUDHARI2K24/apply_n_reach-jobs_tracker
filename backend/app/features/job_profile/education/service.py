"""Service functions for the job_profile education sub-feature."""
import json
import asyncpg
from fastapi import HTTPException, status

from app.features.core.query_helpers import build_partial_update_query
from app.features.job_profile.education import models
from app.features.job_profile.education.schemas import (
    JPEducationCreate,
    JPEducationUpdate,
    _parse_month_year,
)
from app.features.job_profile.import_helpers import (
    validate_source_ownership,
    get_already_imported,
)
from app.features.job_profile.import_schemas import ImportResult


async def list_educations(
    conn: asyncpg.Connection, job_profile_id: int
) -> list[asyncpg.Record]:
    """List all education entries for a job profile, ordered by start_month_year DESC."""
    await models.ensure_jp_education_schema(conn)
    return await conn.fetch(
        "SELECT * FROM job_profile_educations WHERE job_profile_id = $1 "
        "ORDER BY start_month_year DESC",
        job_profile_id,
    )


async def get_education(
    conn: asyncpg.Connection, job_profile_id: int, education_id: int
) -> asyncpg.Record:
    """Fetch a single education entry, verifying ownership via job_profile_id."""
    await models.ensure_jp_education_schema(conn)
    row = await conn.fetchrow(
        "SELECT * FROM job_profile_educations WHERE id = $1 AND job_profile_id = $2",
        education_id,
        job_profile_id,
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education entry not found",
        )
    return row


async def add_education(
    conn: asyncpg.Connection, job_profile_id: int, data: JPEducationCreate
) -> asyncpg.Record:
    """Create a new education entry for a job profile."""
    await models.ensure_jp_education_schema(conn)
    return await conn.fetchrow(
        "INSERT INTO job_profile_educations "
        "(job_profile_id, source_education_id, university_name, major, degree_type, "
        "start_month_year, end_month_year, bullet_points, reference_links) "
        "VALUES ($1, NULL, $2, $3, $4, $5, $6, $7::jsonb, $8::jsonb) "
        "RETURNING *",
        job_profile_id,
        data.university_name,
        data.major,
        data.degree_type,
        data.start_month_year,
        data.end_month_year,
        json.dumps(data.bullet_points),
        json.dumps(data.reference_links),
    )


async def update_education(
    conn: asyncpg.Connection,
    job_profile_id: int,
    education_id: int,
    data: JPEducationUpdate,
) -> asyncpg.Record:
    """Partially update an existing education entry."""
    await models.ensure_jp_education_schema(conn)
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Cross-validate dates when only one is provided in the update
    has_start = "start_month_year" in updates
    has_end = "end_month_year" in updates
    if has_start ^ has_end:
        existing = await conn.fetchrow(
            "SELECT start_month_year, end_month_year FROM job_profile_educations "
            "WHERE id = $1 AND job_profile_id = $2",
            education_id,
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
        "job_profile_educations",
        {"id": education_id, "job_profile_id": job_profile_id},
        updates,
        jsonb_fields={"bullet_points", "reference_links"},
    )
    row = await conn.fetchrow(query, *params)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education entry not found",
        )
    return row


async def delete_education(
    conn: asyncpg.Connection, job_profile_id: int, education_id: int
) -> None:
    """Delete an education entry, verifying ownership."""
    await models.ensure_jp_education_schema(conn)
    result = await conn.execute(
        "DELETE FROM job_profile_educations WHERE id = $1 AND job_profile_id = $2",
        education_id,
        job_profile_id,
    )
    affected = int(result.split()[-1])
    if affected == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education entry not found",
        )


async def import_educations_from_profile(
    conn: asyncpg.Connection,
    job_profile_id: int,
    user_id: int,
    source_ids: list[int],
) -> ImportResult:
    """Import education entries from the user's master profile into a job profile."""
    await models.ensure_jp_education_schema(conn)

    valid_ids, not_found_ids = await validate_source_ownership(
        conn, "educations", source_ids, user_id
    )

    if not valid_ids:
        return ImportResult(imported=[], skipped=[], not_found=not_found_ids)

    already_imported = await get_already_imported(
        conn, "job_profile_educations", job_profile_id, "source_education_id", valid_ids
    )
    already_imported_set = set(already_imported)

    to_import = [sid for sid in valid_ids if sid not in already_imported_set]
    skipped_ids = [sid for sid in valid_ids if sid in already_imported_set]

    if not to_import:
        return ImportResult(imported=[], skipped=skipped_ids, not_found=not_found_ids)

    source_rows = await conn.fetch(
        "SELECT * FROM educations WHERE id = ANY($1)", to_import
    )

    imported_ids = []
    async with conn.transaction():
        for row in source_rows:
            bullet_points = row["bullet_points"]
            reference_links = row["reference_links"]
            if not isinstance(bullet_points, str):
                bullet_points = json.dumps(bullet_points)
            if not isinstance(reference_links, str):
                reference_links = json.dumps(reference_links)

            await conn.execute(
                "INSERT INTO job_profile_educations "
                "(job_profile_id, source_education_id, university_name, major, degree_type, "
                "start_month_year, end_month_year, bullet_points, reference_links) "
                "VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9::jsonb)",
                job_profile_id,
                row["id"],
                row["university_name"],
                row["major"],
                row["degree_type"],
                row["start_month_year"],
                row["end_month_year"],
                bullet_points,
                reference_links,
            )
            imported_ids.append(row["id"])

    return ImportResult(imported=imported_ids, skipped=skipped_ids, not_found=not_found_ids)
