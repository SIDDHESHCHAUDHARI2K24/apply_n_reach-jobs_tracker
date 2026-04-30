"""Low-level SQL helpers for the researches table."""

import asyncpg


RESEARCHES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS researches (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    paper_name TEXT NOT NULL,
    publication_link TEXT NOT NULL,
    description TEXT,
    journal TEXT,
    year TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


async def ensure_research_schema(conn: asyncpg.Connection) -> None:
    """Create the researches table if it does not exist."""
    await conn.execute(RESEARCHES_TABLE_SQL)
    await conn.execute("ALTER TABLE researches ADD COLUMN IF NOT EXISTS journal TEXT")
    await conn.execute("ALTER TABLE researches ADD COLUMN IF NOT EXISTS year TEXT")
