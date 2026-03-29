"""Low-level SQL helpers for the skill_items table."""

import asyncpg


SKILL_ITEMS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS skill_items (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    kind TEXT NOT NULL CHECK (kind IN ('technical', 'competency')),
    name TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


async def ensure_skills_schema(conn: asyncpg.Connection) -> None:
    """Create the skill_items table if it does not exist."""
    await conn.execute(SKILL_ITEMS_TABLE_SQL)
