"""Add location column to experiences and job_profile_experiences tables.

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-04-29

"""
from alembic import op

revision = "f6a7b8c9d0e1"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE experiences ADD COLUMN IF NOT EXISTS location TEXT")
    op.execute("ALTER TABLE job_profile_experiences ADD COLUMN IF NOT EXISTS location TEXT")


def downgrade() -> None:
    op.execute("ALTER TABLE experiences DROP COLUMN IF EXISTS location")
    op.execute("ALTER TABLE job_profile_experiences DROP COLUMN IF EXISTS location")
