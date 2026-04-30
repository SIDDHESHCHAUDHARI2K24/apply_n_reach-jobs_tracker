"""add projects technologies

Revision ID: i9j0k1l2m3n4
Revises: f6a7b8c9d0e1
Create Date: 2026-04-30 00:00:00.000000

"""
from alembic import op

revision = "i9j0k1l2m3n4"
down_revision = "h8i9j0k1l2m3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS technologies JSONB NOT NULL DEFAULT '[]'")


def downgrade() -> None:
    op.execute("ALTER TABLE projects DROP COLUMN IF EXISTS technologies")
