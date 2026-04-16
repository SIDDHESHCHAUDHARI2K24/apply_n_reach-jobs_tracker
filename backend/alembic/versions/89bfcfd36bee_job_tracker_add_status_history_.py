"""job_tracker_add_status_history_constraints

Revision ID: 89bfcfd36bee
Revises: b81c3184eb7c
Create Date: 2026-04-16 18:32:13.630232

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '89bfcfd36bee'
down_revision: Union[str, Sequence[str], None] = 'b81c3184eb7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add CHECK constraints on to_status and from_status in job_opening_status_history."""
    op.execute("""
        ALTER TABLE job_opening_status_history
          ADD CONSTRAINT chk_status_history_to_status
          CHECK (to_status IN ('Interested','Applied','Interviewing','Offer','Withdrawn','Rejected'))
    """)
    op.execute("""
        ALTER TABLE job_opening_status_history
          ADD CONSTRAINT chk_status_history_from_status
          CHECK (from_status IN ('Interested','Applied','Interviewing','Offer','Withdrawn','Rejected') OR from_status IS NULL)
    """)


def downgrade() -> None:
    """Drop CHECK constraints on to_status and from_status."""
    op.execute("ALTER TABLE job_opening_status_history DROP CONSTRAINT IF EXISTS chk_status_history_to_status")
    op.execute("ALTER TABLE job_opening_status_history DROP CONSTRAINT IF EXISTS chk_status_history_from_status")
