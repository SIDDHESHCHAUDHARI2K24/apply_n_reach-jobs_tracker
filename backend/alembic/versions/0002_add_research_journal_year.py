"""Add journal and year columns to researches table.

Revision ID: 0002_research_journal_year
Revises:
Create Date: 2026-04-30

"""
from alembic import op

revision = '0002_research_journal_year'
down_revision = None  # coordinator will merge heads
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE researches ADD COLUMN IF NOT EXISTS journal TEXT")
    op.execute("ALTER TABLE researches ADD COLUMN IF NOT EXISTS year TEXT")


def downgrade():
    op.execute("ALTER TABLE researches DROP COLUMN IF EXISTS journal")
    op.execute("ALTER TABLE researches DROP COLUMN IF EXISTS year")
