"""Add journal and year columns to researches table.

Revision ID: h8i9j0k1l2m3
Revises: f6a7b8c9d0e1
Create Date: 2026-04-30

"""
from alembic import op

revision = "h8i9j0k1l2m3"
down_revision = "g7h8i9j0k1l2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE researches ADD COLUMN IF NOT EXISTS journal TEXT")
    op.execute("ALTER TABLE researches ADD COLUMN IF NOT EXISTS year TEXT")


def downgrade() -> None:
    op.execute("ALTER TABLE researches DROP COLUMN IF EXISTS journal")
    op.execute("ALTER TABLE researches DROP COLUMN IF EXISTS year")
