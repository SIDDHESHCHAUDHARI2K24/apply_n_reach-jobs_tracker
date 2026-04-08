"""DDL and schema helpers for the job_profile_researches table."""
import asyncpg


CREATE_JP_RESEARCHES_TABLE = """
CREATE TABLE IF NOT EXISTS job_profile_researches (
    id SERIAL PRIMARY KEY,
    job_profile_id INTEGER NOT NULL REFERENCES job_profiles(id) ON DELETE CASCADE,
    source_research_id INTEGER REFERENCES researches(id) ON DELETE SET NULL,
    paper_name TEXT NOT NULL,
    publication_link TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


async def ensure_jp_research_schema(conn: asyncpg.Connection) -> None:
    """Create the job_profile_researches table if it does not exist."""
    await conn.execute(CREATE_JP_RESEARCHES_TABLE)
