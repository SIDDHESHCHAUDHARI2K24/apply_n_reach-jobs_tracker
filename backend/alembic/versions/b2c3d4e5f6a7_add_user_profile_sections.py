"""add_user_profile_sections

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-29 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all user profile section tables."""
    op.execute("""
    CREATE TABLE IF NOT EXISTS educations (
        id SERIAL PRIMARY KEY,
        profile_id INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
        university_name TEXT NOT NULL,
        major TEXT NOT NULL,
        degree_type TEXT NOT NULL,
        start_month_year TEXT NOT NULL,
        end_month_year TEXT,
        bullet_points JSONB NOT NULL DEFAULT '[]',
        reference_links JSONB NOT NULL DEFAULT '[]',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)
    op.execute("""
    CREATE TABLE IF NOT EXISTS experiences (
        id SERIAL PRIMARY KEY,
        profile_id INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
        role_title TEXT NOT NULL,
        company_name TEXT NOT NULL,
        start_month_year TEXT NOT NULL,
        end_month_year TEXT,
        context TEXT NOT NULL DEFAULT '',
        work_sample_links JSONB NOT NULL DEFAULT '[]',
        bullet_points JSONB NOT NULL DEFAULT '[]',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)
    op.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id SERIAL PRIMARY KEY,
        profile_id INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
        project_name TEXT NOT NULL,
        description TEXT NOT NULL DEFAULT '',
        start_month_year TEXT NOT NULL,
        end_month_year TEXT,
        reference_links JSONB NOT NULL DEFAULT '[]',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)
    op.execute("""
    CREATE TABLE IF NOT EXISTS researches (
        id SERIAL PRIMARY KEY,
        profile_id INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
        paper_name TEXT NOT NULL,
        publication_link TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)
    op.execute("""
    CREATE TABLE IF NOT EXISTS skill_items (
        id SERIAL PRIMARY KEY,
        profile_id INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
        kind TEXT NOT NULL CHECK (kind IN ('technical', 'competency')),
        name TEXT NOT NULL,
        sort_order INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)
    op.execute("""
    CREATE TABLE IF NOT EXISTS certifications (
        id SERIAL PRIMARY KEY,
        profile_id INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
        certification_name TEXT NOT NULL,
        verification_link TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)


def downgrade() -> None:
    """Drop all user profile section tables in reverse FK order."""
    op.execute("DROP TABLE IF EXISTS certifications")
    op.execute("DROP TABLE IF EXISTS skill_items")
    op.execute("DROP TABLE IF EXISTS researches")
    op.execute("DROP TABLE IF EXISTS projects")
    op.execute("DROP TABLE IF EXISTS experiences")
    op.execute("DROP TABLE IF EXISTS educations")
