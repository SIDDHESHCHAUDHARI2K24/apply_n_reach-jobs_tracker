"""Low-level SQL helpers for the experiences table."""

import asyncpg

from app.features.user_profile.personal.models import ensure_profile_schema


EXPERIENCES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS experiences (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
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


async def ensure_experience_schema(conn: asyncpg.Connection) -> None:
    """Create user_profiles, personal_details, and experiences tables if they do not exist."""
    await ensure_profile_schema(conn)
    await conn.execute(EXPERIENCES_TABLE_SQL)
