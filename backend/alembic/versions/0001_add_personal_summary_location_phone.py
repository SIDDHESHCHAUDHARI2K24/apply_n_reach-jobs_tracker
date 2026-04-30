"""add_personal_summary_location_phone

Revision ID: 0001_personal_summary_location_phone
Revises:
Create Date: 2026-04-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '0001_personal_summary_location_phone'
down_revision: Union[str, Sequence[str], None] = None  # coordinator will merge heads
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE personal_details ADD COLUMN IF NOT EXISTS summary TEXT")
    op.execute("ALTER TABLE personal_details ADD COLUMN IF NOT EXISTS location TEXT")
    op.execute("ALTER TABLE personal_details ADD COLUMN IF NOT EXISTS phone TEXT")


def downgrade() -> None:
    op.execute("ALTER TABLE personal_details DROP COLUMN IF EXISTS summary")
    op.execute("ALTER TABLE personal_details DROP COLUMN IF EXISTS location")
    op.execute("ALTER TABLE personal_details DROP COLUMN IF EXISTS phone")
