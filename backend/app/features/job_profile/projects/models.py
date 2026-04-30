"""DDL and schema helpers for the job_profile_projects table."""
import asyncpg


CREATE_JP_PROJECTS_TABLE = """
CREATE TABLE IF NOT EXISTS job_profile_projects (
    id SERIAL PRIMARY KEY,
    job_profile_id INTEGER NOT NULL REFERENCES job_profiles(id) ON DELETE CASCADE,
    source_project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    project_name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    start_month_year TEXT,
    end_month_year TEXT,
    reference_links JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


async def ensure_jp_projects_schema(conn: asyncpg.Connection) -> None:
    """Create the job_profile_projects table if it does not exist."""
    await conn.execute(CREATE_JP_PROJECTS_TABLE)
    await conn.execute(
        "ALTER TABLE job_profile_projects ADD COLUMN IF NOT EXISTS technologies JSONB NOT NULL DEFAULT '[]'"
    )
