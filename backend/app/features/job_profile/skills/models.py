"""DDL and schema helpers for the job_profile_skill_items table."""
import asyncpg


CREATE_JP_SKILL_ITEMS_TABLE = """
CREATE TABLE IF NOT EXISTS job_profile_skill_items (
    id SERIAL PRIMARY KEY,
    job_profile_id INTEGER NOT NULL REFERENCES job_profiles(id) ON DELETE CASCADE,
    kind TEXT NOT NULL CHECK (kind IN ('technical', 'competency')),
    name TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


async def ensure_jp_skills_schema(conn: asyncpg.Connection) -> None:
    """Create the job_profile_skill_items table if it does not exist."""
    await conn.execute(CREATE_JP_SKILL_ITEMS_TABLE)
