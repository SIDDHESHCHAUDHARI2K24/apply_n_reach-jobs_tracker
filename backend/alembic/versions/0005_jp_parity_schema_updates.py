"""JP parity schema updates: add summary/location/phone to jp_personal,
journal/year to jp_researches, and technologies to jp_projects.

Revision ID: 0005_jp_parity_schema_updates
Revises: i9j0k1l2m3n4
Create Date: 2026-04-30

"""
from alembic import op

revision = "0005_jp_parity_schema_updates"
down_revision = "i9j0k1l2m3n4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # JP personal details — mirror user-profile B1 parity fields
    op.execute(
        "ALTER TABLE job_profile_personal_details ADD COLUMN IF NOT EXISTS summary TEXT"
    )
    op.execute(
        "ALTER TABLE job_profile_personal_details ADD COLUMN IF NOT EXISTS location TEXT"
    )
    op.execute(
        "ALTER TABLE job_profile_personal_details ADD COLUMN IF NOT EXISTS phone TEXT"
    )

    # JP research — mirror user-profile B2 parity fields
    op.execute(
        "ALTER TABLE job_profile_researches ADD COLUMN IF NOT EXISTS journal TEXT"
    )
    op.execute(
        "ALTER TABLE job_profile_researches ADD COLUMN IF NOT EXISTS year TEXT"
    )

    # JP projects — mirror user-profile B3 technologies field
    op.execute(
        "ALTER TABLE job_profile_projects ADD COLUMN IF NOT EXISTS "
        "technologies JSONB NOT NULL DEFAULT '[]'"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE job_profile_projects DROP COLUMN IF EXISTS technologies"
    )
    op.execute(
        "ALTER TABLE job_profile_researches DROP COLUMN IF EXISTS year"
    )
    op.execute(
        "ALTER TABLE job_profile_researches DROP COLUMN IF EXISTS journal"
    )
    op.execute(
        "ALTER TABLE job_profile_personal_details DROP COLUMN IF EXISTS phone"
    )
    op.execute(
        "ALTER TABLE job_profile_personal_details DROP COLUMN IF EXISTS location"
    )
    op.execute(
        "ALTER TABLE job_profile_personal_details DROP COLUMN IF EXISTS summary"
    )
