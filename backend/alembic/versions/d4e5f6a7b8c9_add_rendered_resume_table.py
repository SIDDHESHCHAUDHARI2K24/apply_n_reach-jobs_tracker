"""add_rendered_resume_table

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-04-15 12:00:00.000000
"""
from typing import Sequence, Union
from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
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
    )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS rendered_resume CASCADE")
