"""Service functions for the certifications sub-feature."""
import asyncpg
from fastapi import HTTPException, status

from app.features.user_profile.certifications import models
from app.features.user_profile.certifications.schemas import CertificationCreate


async def list_certifications(conn: asyncpg.Connection, profile_id: int) -> list[asyncpg.Record]:
    """List all certification entries for a profile, ordered by created_at DESC."""
    await models.ensure_certifications_schema(conn)
    return await conn.fetch(
        "SELECT id, profile_id, certification_name, verification_link, "
        "created_at, updated_at FROM certifications WHERE profile_id = $1 "
        "ORDER BY created_at DESC",
        profile_id,
    )


async def get_certification(
    conn: asyncpg.Connection, profile_id: int, certification_id: int
) -> asyncpg.Record:
    """Fetch a single certification entry, verifying ownership."""
    await models.ensure_certifications_schema(conn)
    row = await conn.fetchrow(
        "SELECT id, profile_id, certification_name, verification_link, "
        "created_at, updated_at FROM certifications WHERE id = $1 AND profile_id = $2",
        certification_id,
        profile_id,
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certification not found")
    return row


async def add_certification(
    conn: asyncpg.Connection, profile_id: int, data: CertificationCreate
) -> asyncpg.Record:
    """Create a new certification entry for a profile."""
    await models.ensure_certifications_schema(conn)
    return await conn.fetchrow(
        "INSERT INTO certifications (profile_id, certification_name, verification_link) "
        "VALUES ($1, $2, $3) "
        "RETURNING id, profile_id, certification_name, verification_link, "
        "created_at, updated_at",
        profile_id,
        data.certification_name,
        data.verification_link,
    )


async def update_certification(
    conn: asyncpg.Connection, profile_id: int, certification_id: int, data: CertificationCreate
) -> asyncpg.Record:
    """Update an existing certification entry, verifying ownership."""
    await models.ensure_certifications_schema(conn)
    row = await conn.fetchrow(
        "UPDATE certifications SET certification_name=$1, verification_link=$2, updated_at=NOW() "
        "WHERE id=$3 AND profile_id=$4 "
        "RETURNING id, profile_id, certification_name, verification_link, "
        "created_at, updated_at",
        data.certification_name,
        data.verification_link,
        certification_id,
        profile_id,
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certification not found")
    return row


async def delete_certification(
    conn: asyncpg.Connection, profile_id: int, certification_id: int
) -> None:
    """Delete a certification entry, verifying ownership."""
    await models.ensure_certifications_schema(conn)
    result = await conn.execute(
        "DELETE FROM certifications WHERE id = $1 AND profile_id = $2",
        certification_id,
        profile_id,
    )
    affected = int(result.split()[-1])
    if affected == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certification not found")
