"""Service functions for the skills sub-feature."""
import asyncpg
from fastapi import HTTPException, status

from app.features.user_profile.skills import models
from app.features.user_profile.skills.schemas import SkillsUpdate


async def list_skills(conn: asyncpg.Connection, profile_id: int) -> list[asyncpg.Record]:
    """List all skill items for a profile, ordered by sort_order then name."""
    await models.ensure_skills_schema(conn)
    return await conn.fetch(
        "SELECT id, profile_id, kind, name, sort_order, created_at "
        "FROM skill_items WHERE profile_id = $1 ORDER BY sort_order ASC, name ASC",
        profile_id,
    )


async def get_skill(
    conn: asyncpg.Connection, profile_id: int, skill_id: int
) -> asyncpg.Record:
    """Fetch a single skill item, verifying ownership."""
    await models.ensure_skills_schema(conn)
    row = await conn.fetchrow(
        "SELECT id, profile_id, kind, name, sort_order, created_at "
        "FROM skill_items WHERE id = $1 AND profile_id = $2",
        skill_id,
        profile_id,
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return row


async def replace_skills(
    conn: asyncpg.Connection, profile_id: int, data: SkillsUpdate
) -> list[asyncpg.Record]:
    """Replace the full skill set for a profile (transactional delete-then-insert).

    Deletes all existing skill_items for the profile, then inserts the new set.
    Returns the newly inserted rows ordered by sort_order ASC, name ASC.

    Args:
        conn: Active asyncpg connection.
        profile_id: The profile's id.
        data: SkillsUpdate with the desired skill list.

    Returns:
        List of newly created skill_item rows.
    """
    await models.ensure_skills_schema(conn)
    async with conn.transaction():
        await conn.execute("DELETE FROM skill_items WHERE profile_id = $1", profile_id)
        if data.skills:
            await conn.executemany(
                "INSERT INTO skill_items (profile_id, kind, name, sort_order) VALUES ($1, $2, $3, $4)",
                [(profile_id, s.kind, s.name, s.sort_order) for s in data.skills],
            )
    return await list_skills(conn, profile_id)
