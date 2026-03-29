"""Low-level SQL helpers for the projects table."""

import asyncpg


PROJECTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    project_name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    start_month_year TEXT NOT NULL,
    end_month_year TEXT,
    reference_links JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


async def ensure_projects_schema(conn: asyncpg.Connection) -> None:
    """Create the projects table if it does not exist."""
    await conn.execute(PROJECTS_TABLE_SQL)
