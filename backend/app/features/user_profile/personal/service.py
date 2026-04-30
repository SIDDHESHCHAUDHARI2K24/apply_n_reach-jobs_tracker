"""Service functions for UserProfile and PersonalDetails."""
import asyncpg
from fastapi import HTTPException, status

from app.features.user_profile.personal import models
from app.features.user_profile.personal.schemas import PersonalDetailsCreate


async def create_profile(conn: asyncpg.Connection, user_id: int) -> asyncpg.Record:
    """Create a new UserProfile for the given user_id.

    Args:
        conn: Active asyncpg connection.
        user_id: The authenticated user's ID.

    Returns:
        The newly created user_profile row.

    Raises:
        HTTPException(409): If a profile already exists for this user.
    """
    await models.ensure_profile_schema(conn)
    existing = await conn.fetchrow(
        "SELECT id FROM user_profiles WHERE user_id = $1", user_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists",
        )
    return await conn.fetchrow(
        "INSERT INTO user_profiles (user_id) VALUES ($1) "
        "RETURNING id, user_id, created_at, updated_at",
        user_id,
    )


async def get_personal_details(conn: asyncpg.Connection, profile_id: int) -> asyncpg.Record | None:
    """Fetch the PersonalDetails row for a profile.

    Args:
        conn: Active asyncpg connection.
        profile_id: The profile's id.

    Returns:
        The personal_details row, or None if not yet created.
    """
    await models.ensure_profile_schema(conn)
    return await conn.fetchrow(
        "SELECT id, profile_id, full_name, email, linkedin_url, github_url, portfolio_url, "
        "summary, location, phone "
        "FROM personal_details WHERE profile_id = $1",
        profile_id,
    )


async def upsert_personal_details(
    conn: asyncpg.Connection, profile_id: int, data: PersonalDetailsCreate
) -> asyncpg.Record:
    """Insert or update PersonalDetails for a profile.

    Args:
        conn: Active asyncpg connection.
        profile_id: The profile's id.
        data: Validated PersonalDetailsCreate schema.

    Returns:
        The upserted personal_details row.
    """
    await models.ensure_profile_schema(conn)
    return await conn.fetchrow(
        """
        INSERT INTO personal_details (profile_id, full_name, email, linkedin_url, github_url, portfolio_url, summary, location, phone)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ON CONFLICT (profile_id) DO UPDATE SET
            full_name = EXCLUDED.full_name,
            email = EXCLUDED.email,
            linkedin_url = EXCLUDED.linkedin_url,
            github_url = EXCLUDED.github_url,
            portfolio_url = EXCLUDED.portfolio_url,
            summary = EXCLUDED.summary,
            location = EXCLUDED.location,
            phone = EXCLUDED.phone
        RETURNING id, profile_id, full_name, email, linkedin_url, github_url, portfolio_url, summary, location, phone
        """,
        profile_id,
        data.full_name,
        str(data.email),
        data.linkedin_url,
        data.github_url,
        data.portfolio_url,
        data.summary,
        data.location,
        data.phone,
    )
