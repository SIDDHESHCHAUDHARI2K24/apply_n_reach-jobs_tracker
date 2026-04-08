"""DDL and schema helpers for the job_profile_experiences table."""
import asyncpg


CREATE_JP_EXPERIENCES_TABLE = """
CREATE TABLE IF NOT EXISTS job_profile_experiences (
    id SERIAL PRIMARY KEY,
    job_profile_id INTEGER NOT NULL REFERENCES job_profiles(id) ON DELETE CASCADE,
    source_experience_id INTEGER REFERENCES experiences(id) ON DELETE SET NULL,
    role_title TEXT NOT NULL,
    company_name TEXT NOT NULL,
    start_month_year TEXT NOT NULL,
    end_month_year TEXT,
    context TEXT NOT NULL DEFAULT '',
    work_sample_links JSONB NOT NULL DEFAULT '[]',
    bullet_points JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


async def ensure_jp_experience_schema(conn: asyncpg.Connection) -> None:
    """Create the job_profile_experiences table if it does not exist."""
    await conn.execute(CREATE_JP_EXPERIENCES_TABLE)
