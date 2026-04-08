"""Service functions for UserProfile and PersonalDetails."""
import asyncpg
from fastapi import HTTPException, status

from app.features.core.query_helpers import build_partial_update_query
from app.features.user_profile.personal import models
from app.features.user_profile.personal.schemas import PersonalDetailsCreate, PersonalDetailsUpdate


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
        "SELECT id, profile_id, full_name, email, linkedin_url, github_url, portfolio_url "
        "FROM personal_details WHERE profile_id = $1",
        profile_id,
    )


async def update_personal_details(
    conn: asyncpg.Connection, profile_id: int, data: PersonalDetailsUpdate
) -> asyncpg.Record:
    """Partial update of personal details. Row must exist."""
    await models.ensure_profile_schema(conn)
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Convert email to string if present
    if "email" in updates and updates["email"] is not None:
        updates["email"] = str(updates["email"])

    query, params = build_partial_update_query(
        "personal_details",
        {"profile_id": profile_id},
        updates
    )
    row = await conn.fetchrow(query, *params)
    if row is None:
        raise HTTPException(status_code=404, detail="Personal details not found. Create them first.")
    return row


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
        INSERT INTO personal_details (profile_id, full_name, email, linkedin_url, github_url, portfolio_url)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (profile_id) DO UPDATE SET
            full_name = EXCLUDED.full_name,
            email = EXCLUDED.email,
            linkedin_url = EXCLUDED.linkedin_url,
            github_url = EXCLUDED.github_url,
            portfolio_url = EXCLUDED.portfolio_url,
            updated_at = NOW()
        RETURNING id, profile_id, full_name, email, linkedin_url, github_url, portfolio_url
        """,
        profile_id,
        data.full_name,
        str(data.email),
        data.linkedin_url,
        data.github_url,
        data.portfolio_url,
    )


async def get_profile_summary(conn: asyncpg.Connection, profile_id: int) -> asyncpg.Record:
    """Get counts/existence for all profile sections in a single query."""
    from app.features.user_profile.education.models import ensure_education_schema
    from app.features.user_profile.experience.models import ensure_experience_schema
    from app.features.user_profile.projects.models import ensure_projects_schema
    from app.features.user_profile.research.models import ensure_research_schema
    from app.features.user_profile.certifications.models import ensure_certifications_schema
    from app.features.user_profile.skills.models import ensure_skills_schema

    await models.ensure_profile_schema(conn)
    await ensure_education_schema(conn)
    await ensure_experience_schema(conn)
    await ensure_projects_schema(conn)
    await ensure_research_schema(conn)
    await ensure_certifications_schema(conn)
    await ensure_skills_schema(conn)

    return await conn.fetchrow(
        """
        SELECT
            EXISTS(SELECT 1 FROM personal_details WHERE profile_id = $1) AS personal_details_exists,
            (SELECT COUNT(*) FROM educations WHERE profile_id = $1) AS education_count,
            (SELECT COUNT(*) FROM experiences WHERE profile_id = $1) AS experience_count,
            (SELECT COUNT(*) FROM projects WHERE profile_id = $1) AS projects_count,
            (SELECT COUNT(*) FROM researches WHERE profile_id = $1) AS research_count,
            (SELECT COUNT(*) FROM certifications WHERE profile_id = $1) AS certifications_count,
            (SELECT COUNT(*) FROM skill_items WHERE profile_id = $1) AS skills_count
        """,
        profile_id
    )
