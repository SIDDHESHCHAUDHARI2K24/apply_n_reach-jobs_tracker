"""Low-level SQL helpers for the educations table."""

import asyncpg


EDUCATIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS educations (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
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


async def ensure_education_schema(conn: asyncpg.Connection) -> None:
    """Create the educations table if it does not exist."""
    await conn.execute(EDUCATIONS_TABLE_SQL)
