"""Add JSONB columns to opening resume sections for job-profile parity.

Revision ID: n3o4p5q6r7s8
Revises: m1n2o3p4q5r6
Create Date: 2026-05-04

- job_opening_education: bullet_points, reference_links
- job_opening_experience: bullet_points, work_sample_links
- job_opening_projects: reference_links
"""
from typing import Sequence, Union

from alembic import op

revision: str = "n3o4p5q6r7s8"
down_revision: Union[str, Sequence[str], None] = "m1n2o3p4q5r6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE job_opening_education "
        "ADD COLUMN IF NOT EXISTS bullet_points JSONB NOT NULL DEFAULT '[]'::jsonb"
    )
    op.execute(
        "ALTER TABLE job_opening_education "
        "ADD COLUMN IF NOT EXISTS reference_links JSONB NOT NULL DEFAULT '[]'::jsonb"
    )
    op.execute(
        "ALTER TABLE job_opening_experience "
        "ADD COLUMN IF NOT EXISTS bullet_points JSONB NOT NULL DEFAULT '[]'::jsonb"
    )
    op.execute(
        "ALTER TABLE job_opening_experience "
        "ADD COLUMN IF NOT EXISTS work_sample_links JSONB NOT NULL DEFAULT '[]'::jsonb"
    )
    op.execute(
        "ALTER TABLE job_opening_projects "
        "ADD COLUMN IF NOT EXISTS reference_links JSONB NOT NULL DEFAULT '[]'::jsonb"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE job_opening_projects DROP COLUMN IF EXISTS reference_links"
    )
    op.execute(
        "ALTER TABLE job_opening_experience DROP COLUMN IF EXISTS work_sample_links"
    )
    op.execute(
        "ALTER TABLE job_opening_experience DROP COLUMN IF EXISTS bullet_points"
    )
    op.execute(
        "ALTER TABLE job_opening_education DROP COLUMN IF EXISTS reference_links"
    )
    op.execute(
        "ALTER TABLE job_opening_education DROP COLUMN IF EXISTS bullet_points"
    )
