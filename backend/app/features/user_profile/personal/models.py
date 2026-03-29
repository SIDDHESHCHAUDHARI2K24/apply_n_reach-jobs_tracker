"""Low-level SQL helpers for user_profiles and personal_details tables."""

import asyncpg


USER_PROFILES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

PERSONAL_DETAILS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS personal_details (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL UNIQUE REFERENCES user_profiles(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    linkedin_url TEXT NOT NULL,
    github_url TEXT,
    portfolio_url TEXT
);
"""


async def ensure_profile_schema(conn: asyncpg.Connection) -> None:
    """Create user_profiles and personal_details tables if they do not exist."""
    await conn.execute(USER_PROFILES_TABLE_SQL)
    await conn.execute(PERSONAL_DETAILS_TABLE_SQL)
