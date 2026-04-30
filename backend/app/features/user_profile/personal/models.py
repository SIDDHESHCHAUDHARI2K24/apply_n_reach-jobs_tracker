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
    portfolio_url TEXT,
    summary TEXT,
    location TEXT,
    phone TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


async def ensure_profile_schema(conn: asyncpg.Connection) -> None:
    """Create user_profiles and personal_details tables if they do not exist."""
    await conn.execute(USER_PROFILES_TABLE_SQL)
    await conn.execute(PERSONAL_DETAILS_TABLE_SQL)
    await conn.execute("ALTER TABLE personal_details ADD COLUMN IF NOT EXISTS summary TEXT")
    await conn.execute("ALTER TABLE personal_details ADD COLUMN IF NOT EXISTS location TEXT")
    await conn.execute("ALTER TABLE personal_details ADD COLUMN IF NOT EXISTS phone TEXT")
    await conn.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'personal_details' AND column_name = 'updated_at'
            ) THEN
                ALTER TABLE personal_details
                ADD COLUMN updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
            END IF;
        END $$;
        """
    )
