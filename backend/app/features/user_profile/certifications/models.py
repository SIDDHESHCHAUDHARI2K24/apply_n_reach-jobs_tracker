"""Low-level SQL helpers for the certifications table."""

import asyncpg


CERTIFICATIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS certifications (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    certification_name TEXT NOT NULL,
    verification_link TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


async def ensure_certifications_schema(conn: asyncpg.Connection) -> None:
    """Create the certifications table if it does not exist."""
    await conn.execute(CERTIFICATIONS_TABLE_SQL)
