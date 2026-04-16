"""DDL reference constants for job_tracker openings tables.

These SQL strings are for documentation/reference only.
Actual tables are created and managed via Alembic migrations.
"""
import asyncpg


CREATE_JOB_OPENINGS_TABLE = """
CREATE TABLE job_openings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_profile_id INTEGER REFERENCES job_profiles(id) ON DELETE SET NULL,
    source_url TEXT,
    company_name TEXT NOT NULL,
    role_name TEXT NOT NULL,
    current_status TEXT NOT NULL DEFAULT 'Interested'
        CHECK (current_status IN ('Interested','Applied','Interviewing','Offer','Withdrawn','Rejected')),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""

CREATE_STATUS_HISTORY_TABLE = """
CREATE TABLE job_opening_status_history (
    id SERIAL PRIMARY KEY,
    opening_id INTEGER NOT NULL REFERENCES job_openings(id) ON DELETE CASCADE,
    from_status TEXT,
    to_status TEXT NOT NULL,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    changed_by_user_id INTEGER NOT NULL REFERENCES users(id)
)
"""


async def ensure_openings_schema(conn: asyncpg.Connection) -> None:
    """No-op: tables managed by Alembic migrations."""
    pass
