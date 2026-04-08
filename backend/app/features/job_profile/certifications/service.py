"""Service functions for the job_profile certifications sub-feature."""
import asyncpg
from fastapi import HTTPException, status

from app.features.core.query_helpers import build_partial_update_query
from app.features.job_profile.certifications import models
from app.features.job_profile.certifications.schemas import (
    JPCertificationCreate,
    JPCertificationUpdate,
)
from app.features.job_profile.import_helpers import (
    validate_source_ownership,
    get_already_imported,
)
from app.features.job_profile.import_schemas import ImportResult


async def list_certifications(
    conn: asyncpg.Connection, job_profile_id: int
) -> list[asyncpg.Record]:
    """List all certification entries for a job profile, ordered by created_at DESC."""
    await models.ensure_jp_certifications_schema(conn)
    return await conn.fetch(
        "SELECT * FROM job_profile_certifications WHERE job_profile_id = $1 "
        "ORDER BY created_at DESC",
        job_profile_id,
    )


async def get_certification(
    conn: asyncpg.Connection, job_profile_id: int, cert_id: int
) -> asyncpg.Record:
    """Fetch a single certification entry, verifying ownership via job_profile_id."""
    await models.ensure_jp_certifications_schema(conn)
    row = await conn.fetchrow(
        "SELECT * FROM job_profile_certifications WHERE id = $1 AND job_profile_id = $2",
        cert_id,
        job_profile_id,
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification entry not found",
        )
    return row


async def add_certification(
    conn: asyncpg.Connection, job_profile_id: int, data: JPCertificationCreate
) -> asyncpg.Record:
    """Create a new certification entry for a job profile."""
    await models.ensure_jp_certifications_schema(conn)
    row = await conn.fetchrow(
        "INSERT INTO job_profile_certifications "
        "(job_profile_id, certification_name, verification_link) "
        "VALUES ($1, $2, $3) RETURNING *",
        job_profile_id,
        data.certification_name,
        data.verification_link,
    )
    return row


async def update_certification(
    conn: asyncpg.Connection,
    job_profile_id: int,
    cert_id: int,
    data: JPCertificationUpdate,
) -> asyncpg.Record:
    """Partially update an existing certification entry, verifying ownership."""
    await models.ensure_jp_certifications_schema(conn)
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    query, params = build_partial_update_query(
        "job_profile_certifications",
        {"id": cert_id, "job_profile_id": job_profile_id},
        updates,
    )
    row = await conn.fetchrow(query, *params)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification entry not found",
        )
    return row


async def delete_certification(
    conn: asyncpg.Connection, job_profile_id: int, cert_id: int
) -> None:
    """Delete a certification entry, verifying ownership."""
    await models.ensure_jp_certifications_schema(conn)
    result = await conn.execute(
        "DELETE FROM job_profile_certifications WHERE id = $1 AND job_profile_id = $2",
        cert_id,
        job_profile_id,
    )
    affected = int(result.split()[-1])
    if affected == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification entry not found",
        )


async def import_certifications_from_profile(
    conn: asyncpg.Connection,
    job_profile_id: int,
    user_id: int,
    source_ids: list[int],
) -> ImportResult:
    """Import certification entries from the user's master profile into a job profile."""
    await models.ensure_jp_certifications_schema(conn)

    # 1. Validate source ownership
    valid_ids, not_found_ids = await validate_source_ownership(
        conn, "certifications", source_ids, user_id
    )

    if not valid_ids:
        return ImportResult(imported=[], skipped=[], not_found=not_found_ids)

    # 2. Detect already-imported IDs
    already_imported = await get_already_imported(
        conn,
        "job_profile_certifications",
        job_profile_id,
        "source_certification_id",
        valid_ids,
    )
    already_imported_set = set(already_imported)

    to_import = [sid for sid in valid_ids if sid not in already_imported_set]
    skipped_ids = [sid for sid in valid_ids if sid in already_imported_set]

    if not to_import:
        return ImportResult(imported=[], skipped=skipped_ids, not_found=not_found_ids)

    # 3. Fetch source rows
    source_rows = await conn.fetch(
        "SELECT * FROM certifications WHERE id = ANY($1)",
        to_import,
    )

    # 4. Insert each row within a transaction
    imported_ids = []
    async with conn.transaction():
        for row in source_rows:
            await conn.fetchrow(
                "INSERT INTO job_profile_certifications "
                "(job_profile_id, source_certification_id, certification_name, verification_link) "
                "VALUES ($1, $2, $3, $4) "
                "RETURNING id",
                job_profile_id,
                row["id"],
                row["certification_name"],
                row["verification_link"],
            )
            imported_ids.append(row["id"])

    # 5. Return ImportResult
    return ImportResult(
        imported=imported_ids,
        skipped=skipped_ids,
        not_found=not_found_ids,
    )
