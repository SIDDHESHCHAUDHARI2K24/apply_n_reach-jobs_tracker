"""DDL and schema helpers for the rendered_resume table."""
import asyncpg


CREATE_RENDERED_RESUME_TABLE = """
CREATE TABLE IF NOT EXISTS rendered_resume (
    id SERIAL PRIMARY KEY,
    job_profile_id INTEGER NOT NULL UNIQUE REFERENCES job_profiles(id) ON DELETE CASCADE,
    latex_source TEXT NOT NULL,
    pdf_content BYTEA NOT NULL,
    layout_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    template_name TEXT NOT NULL DEFAULT 'jakes_resume_v1',
    rendered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


async def ensure_rendered_resume_schema(conn: asyncpg.Connection) -> None:
    """Create the rendered_resume table if it does not exist."""
    await conn.execute(CREATE_RENDERED_RESUME_TABLE)
