"""drop salary_range from job_opening_extracted_details_versions

Revision ID: m1n2o3p4q5r6
Revises: j0j1k2l3m4n5
Create Date: 2026-05-04

"""
from alembic import op

revision = "m1n2o3p4q5r6"
down_revision = "j0j1k2l3m4n5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE job_opening_extracted_details_versions
            DROP COLUMN IF EXISTS salary_range
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE job_opening_extracted_details_versions
            ADD COLUMN salary_range TEXT
        """
    )
