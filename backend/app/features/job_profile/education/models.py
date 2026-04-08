"""DDL and schema helpers for the job_profile_educations table."""
import asyncpg


CREATE_JP_EDUCATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS job_profile_educations (
    id SERIAL PRIMARY KEY,
    job_profile_id INTEGER NOT NULL REFERENCES job_profiles(id) ON DELETE CASCADE,
    source_education_id INTEGER REFERENCES educations(id) ON DELETE SET NULL,
    university_name TEXT NOT NULL,
    major TEXT NOT NULL,
    degree_type TEXT NOT NULL,
    start_month_year TEXT NOT NULL,
    end_month_year TEXT,
    bullet_points JSONB NOT NULL DEFAULT '[]',
    reference_links JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


async def ensure_jp_education_schema(conn: asyncpg.Connection) -> None:
    """Create the job_profile_educations table if it does not exist."""
    await conn.execute(CREATE_JP_EDUCATIONS_TABLE)
