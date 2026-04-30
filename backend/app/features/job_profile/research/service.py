"""Service functions for the job_profile research sub-feature."""
import asyncpg
from fastapi import HTTPException, status

from app.features.core.query_helpers import build_partial_update_query
from app.features.job_profile.research import models
from app.features.job_profile.research.schemas import JPResearchCreate, JPResearchUpdate
from app.features.job_profile.import_helpers import (
    validate_source_ownership,
    get_already_imported,
)
from app.features.job_profile.import_schemas import ImportResult


async def list_researches(
    conn: asyncpg.Connection, job_profile_id: int
) -> list[asyncpg.Record]:
    """List all research entries for a job profile, ordered by created_at DESC."""
    await models.ensure_jp_research_schema(conn)
    return await conn.fetch(
        "SELECT * FROM job_profile_researches WHERE job_profile_id = $1 "
        "ORDER BY created_at DESC",
        job_profile_id,
    )


async def get_research(
    conn: asyncpg.Connection, job_profile_id: int, research_id: int
) -> asyncpg.Record:
    """Fetch a single research entry, verifying ownership via job_profile_id."""
    await models.ensure_jp_research_schema(conn)
    row = await conn.fetchrow(
        "SELECT * FROM job_profile_researches WHERE id = $1 AND job_profile_id = $2",
        research_id,
        job_profile_id,
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research entry not found",
        )
    return row


async def add_research(
    conn: asyncpg.Connection, job_profile_id: int, data: JPResearchCreate
) -> asyncpg.Record:
    """Create a new research entry for a job profile."""
    await models.ensure_jp_research_schema(conn)
    row = await conn.fetchrow(
        "INSERT INTO job_profile_researches "
        "(job_profile_id, paper_name, publication_link, description, journal, year) "
        "VALUES ($1, $2, $3, $4, $5, $6) RETURNING *",
        job_profile_id,
        data.paper_name,
        data.publication_link,
        data.description,
        data.journal,
        data.year,
    )
    return row


async def update_research(
    conn: asyncpg.Connection,
    job_profile_id: int,
    research_id: int,
    data: JPResearchUpdate,
) -> asyncpg.Record:
    """Partially update an existing research entry, verifying ownership."""
    await models.ensure_jp_research_schema(conn)
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    query, params = build_partial_update_query(
        "job_profile_researches",
        {"id": research_id, "job_profile_id": job_profile_id},
        updates,
    )
    row = await conn.fetchrow(query, *params)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research entry not found",
        )
    return row


async def delete_research(
    conn: asyncpg.Connection, job_profile_id: int, research_id: int
) -> None:
    """Delete a research entry, verifying ownership."""
    await models.ensure_jp_research_schema(conn)
    result = await conn.execute(
        "DELETE FROM job_profile_researches WHERE id = $1 AND job_profile_id = $2",
        research_id,
        job_profile_id,
    )
    affected = int(result.split()[-1])
    if affected == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research entry not found",
        )


async def import_researches_from_profile(
    conn: asyncpg.Connection,
    job_profile_id: int,
    user_id: int,
    source_ids: list[int],
) -> ImportResult:
    """Import research entries from the user's master profile into a job profile."""
    await models.ensure_jp_research_schema(conn)

    # 1. Validate source ownership
    valid_ids, not_found_ids = await validate_source_ownership(
        conn, "researches", source_ids, user_id
    )

    if not valid_ids:
        return ImportResult(imported=[], skipped=[], not_found=not_found_ids)

    # 2. Detect already-imported IDs
    already_imported = await get_already_imported(
        conn,
        "job_profile_researches",
        job_profile_id,
        "source_research_id",
        valid_ids,
    )
    already_imported_set = set(already_imported)

    to_import = [sid for sid in valid_ids if sid not in already_imported_set]
    skipped_ids = [sid for sid in valid_ids if sid in already_imported_set]

    if not to_import:
        return ImportResult(imported=[], skipped=skipped_ids, not_found=not_found_ids)

    # 3. Fetch source rows
    source_rows = await conn.fetch(
        "SELECT * FROM researches WHERE id = ANY($1)",
        to_import,
    )

    # 4. Insert each row within a transaction
    imported_ids = []
    async with conn.transaction():
        for row in source_rows:
            await conn.fetchrow(
                "INSERT INTO job_profile_researches "
                "(job_profile_id, source_research_id, paper_name, publication_link, description, journal, year) "
                "VALUES ($1, $2, $3, $4, $5, $6, $7) "
                "RETURNING id",
                job_profile_id,
                row["id"],
                row["paper_name"],
                row["publication_link"],
                row["description"] or "",
                row.get("journal"),
                row.get("year"),
            )
            imported_ids.append(row["id"])

    # 5. Return ImportResult
    return ImportResult(
        imported=imported_ids,
        skipped=skipped_ids,
        not_found=not_found_ids,
    )
