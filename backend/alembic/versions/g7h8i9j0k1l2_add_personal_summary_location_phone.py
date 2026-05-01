"""add personal summary location phone

Revision ID: g7h8i9j0k1l2
Revises: f6a7b8c9d0e1
Create Date: 2026-04-30

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "g7h8i9j0k1l2"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE personal_details ADD COLUMN IF NOT EXISTS summary TEXT")
    op.execute("ALTER TABLE personal_details ADD COLUMN IF NOT EXISTS location TEXT")
    op.execute("ALTER TABLE personal_details ADD COLUMN IF NOT EXISTS phone TEXT")


def downgrade() -> None:
    op.execute("ALTER TABLE personal_details DROP COLUMN IF EXISTS summary")
    op.execute("ALTER TABLE personal_details DROP COLUMN IF EXISTS location")
    op.execute("ALTER TABLE personal_details DROP COLUMN IF EXISTS phone")
