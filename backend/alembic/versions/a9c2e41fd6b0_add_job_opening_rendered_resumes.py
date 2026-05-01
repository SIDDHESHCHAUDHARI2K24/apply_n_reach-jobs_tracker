"""add_job_opening_rendered_resumes

Revision ID: a9c2e41fd6b0
Revises: 89bfcfd36bee
Create Date: 2026-04-17 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a9c2e41fd6b0"
down_revision: Union[str, Sequence[str], None] = "89bfcfd36bee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create rendered resume table for opening-resume snapshots."""
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS job_opening_rendered_resumes (
            id SERIAL PRIMARY KEY,
            resume_id INTEGER NOT NULL UNIQUE REFERENCES job_opening_resumes(id) ON DELETE CASCADE,
            latex_source TEXT NOT NULL,
            pdf_bytes BYTEA NOT NULL,
            template_name TEXT NOT NULL DEFAULT 'jakes_resume_v1',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_job_opening_rendered_resumes_updated_at "
        "ON job_opening_rendered_resumes(updated_at)"
    )


def downgrade() -> None:
    """Drop rendered resume table for opening resumes."""
    op.execute("DROP INDEX IF EXISTS ix_job_opening_rendered_resumes_updated_at")
    op.execute("DROP TABLE IF EXISTS job_opening_rendered_resumes CASCADE")

