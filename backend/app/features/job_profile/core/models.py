"""DDL and schema helpers for the job_profiles table."""
import asyncpg


CREATE_JOB_PROFILES_TABLE = """
CREATE TABLE IF NOT EXISTS job_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    profile_name TEXT NOT NULL,
    target_role TEXT,
    target_company TEXT,
    job_posting_url TEXT,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'archived')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, profile_name)
);
"""


async def ensure_job_profiles_schema(conn: asyncpg.Connection) -> None:
    """Create the job_profiles table if it does not exist."""
    await conn.execute(CREATE_JOB_PROFILES_TABLE)
