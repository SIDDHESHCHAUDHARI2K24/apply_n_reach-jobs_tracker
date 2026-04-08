"""Service functions for the job_profile personal sub-feature."""
import asyncpg
from fastapi import HTTPException, status

from app.features.core.query_helpers import build_partial_update_query
from app.features.job_profile.personal import models
from app.features.job_profile.personal.schemas import (
    JPPersonalDetailsCreate,
    JPPersonalDetailsUpdate,
)


async def get_personal_details(
    conn: asyncpg.Connection, job_profile_id: int
) -> asyncpg.Record | None:
    """Fetch personal details for a job profile, or None if not yet set."""
    await models.ensure_jp_personal_schema(conn)
    return await conn.fetchrow(
        "SELECT * FROM job_profile_personal_details WHERE job_profile_id = $1",
        job_profile_id,
    )


async def upsert_personal_details(
    conn: asyncpg.Connection, job_profile_id: int, data: JPPersonalDetailsCreate
) -> asyncpg.Record:
    """Insert or update personal details for a job profile (manual entry, no source tracking)."""
    await models.ensure_jp_personal_schema(conn)
    return await conn.fetchrow(
        """
        INSERT INTO job_profile_personal_details
          (job_profile_id, full_name, email, linkedin_url, github_url, portfolio_url)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (job_profile_id) DO UPDATE SET
          full_name = EXCLUDED.full_name,
          email = EXCLUDED.email,
          linkedin_url = EXCLUDED.linkedin_url,
          github_url = EXCLUDED.github_url,
          portfolio_url = EXCLUDED.portfolio_url,
          updated_at = NOW()
        RETURNING *
        """,
        job_profile_id,
        data.full_name,
        str(data.email),
        data.linkedin_url,
        data.github_url,
        data.portfolio_url,
    )


async def update_personal_details(
    conn: asyncpg.Connection, job_profile_id: int, data: JPPersonalDetailsUpdate
) -> asyncpg.Record:
    """Partially update existing personal details."""
    await models.ensure_jp_personal_schema(conn)
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    if "email" in updates and updates["email"] is not None:
        updates["email"] = str(updates["email"])

    query, params = build_partial_update_query(
        "job_profile_personal_details",
        {"job_profile_id": job_profile_id},
        updates,
    )
    row = await conn.fetchrow(query, *params)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal details not found. Create them first.",
        )
    return row


async def import_personal_from_profile(
    conn: asyncpg.Connection, job_profile_id: int, user_id: int
) -> asyncpg.Record:
    """Copy personal details from the user's master profile into the job profile."""
    await models.ensure_jp_personal_schema(conn)

    master = await conn.fetchrow(
        """
        SELECT pd.* FROM personal_details pd
        JOIN user_profiles up ON pd.profile_id = up.id
        WHERE up.user_id = $1
        """,
        user_id,
    )
    if master is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No personal details in master profile to import",
        )

    return await conn.fetchrow(
        """
        INSERT INTO job_profile_personal_details
          (job_profile_id, source_personal_id, full_name, email, linkedin_url,
           github_url, portfolio_url)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (job_profile_id) DO UPDATE SET
          source_personal_id = EXCLUDED.source_personal_id,
          full_name = EXCLUDED.full_name,
          email = EXCLUDED.email,
          linkedin_url = EXCLUDED.linkedin_url,
          github_url = EXCLUDED.github_url,
          portfolio_url = EXCLUDED.portfolio_url,
          updated_at = NOW()
        RETURNING *
        """,
        job_profile_id,
        master["id"],
        master["full_name"],
        master["email"],
        master["linkedin_url"],
        master["github_url"],
        master["portfolio_url"],
    )
