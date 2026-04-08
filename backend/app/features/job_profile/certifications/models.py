"""DDL and schema helpers for the job_profile_certifications table."""
import asyncpg


CREATE_JP_CERTIFICATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS job_profile_certifications (
    id SERIAL PRIMARY KEY,
    job_profile_id INTEGER NOT NULL REFERENCES job_profiles(id) ON DELETE CASCADE,
    source_certification_id INTEGER REFERENCES certifications(id) ON DELETE SET NULL,
    certification_name TEXT NOT NULL,
    verification_link TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


async def ensure_jp_certifications_schema(conn: asyncpg.Connection) -> None:
    """Create the job_profile_certifications table if it does not exist."""
    await conn.execute(CREATE_JP_CERTIFICATIONS_TABLE)
