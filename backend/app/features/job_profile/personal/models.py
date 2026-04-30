"""DDL and schema helpers for the job_profile_personal_details table."""
import asyncpg


CREATE_JP_PERSONAL_TABLE = """
CREATE TABLE IF NOT EXISTS job_profile_personal_details (
    id SERIAL PRIMARY KEY,
    job_profile_id INTEGER NOT NULL UNIQUE REFERENCES job_profiles(id) ON DELETE CASCADE,
    source_personal_id INTEGER REFERENCES personal_details(id) ON DELETE SET NULL,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    linkedin_url TEXT NOT NULL,
    github_url TEXT,
    portfolio_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


async def ensure_jp_personal_schema(conn: asyncpg.Connection) -> None:
    """Create the job_profile_personal_details table if it does not exist."""
    await conn.execute(CREATE_JP_PERSONAL_TABLE)
    await conn.execute(
        "ALTER TABLE job_profile_personal_details ADD COLUMN IF NOT EXISTS summary TEXT"
    )
    await conn.execute(
        "ALTER TABLE job_profile_personal_details ADD COLUMN IF NOT EXISTS location TEXT"
    )
    await conn.execute(
        "ALTER TABLE job_profile_personal_details ADD COLUMN IF NOT EXISTS phone TEXT"
    )
