"""add_job_profile_tables

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-04-06 00:01:00.000000

Creates the job_profiles core table plus all 7 section tables:
- job_profiles (core)
- job_profile_personal_details
- job_profile_educations
- job_profile_experiences
- job_profile_projects
- job_profile_researches
- job_profile_certifications
- job_profile_skill_items
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all job_profile tables."""
    # Core job_profiles table
    op.execute("""
    CREATE TABLE IF NOT EXISTS job_profiles (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        profile_name TEXT NOT NULL,
        target_role TEXT,
        target_company TEXT,
        job_posting_url TEXT,
        status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'archived')),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(user_id, profile_name)
    )
    """)

    # Personal details (1:1 per job_profile)
    op.execute("""
    CREATE TABLE IF NOT EXISTS job_profile_personal_details (
        id SERIAL PRIMARY KEY,
        job_profile_id INTEGER NOT NULL UNIQUE REFERENCES job_profiles(id) ON DELETE CASCADE,
        source_personal_id INTEGER REFERENCES personal_details(id) ON DELETE SET NULL,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        linkedin_url TEXT NOT NULL,
        github_url TEXT,
        portfolio_url TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)

    # Education entries (1:many per job_profile)
    op.execute("""
    CREATE TABLE IF NOT EXISTS job_profile_educations (
        id SERIAL PRIMARY KEY,
        job_profile_id INTEGER NOT NULL REFERENCES job_profiles(id) ON DELETE CASCADE,
        source_education_id INTEGER REFERENCES educations(id) ON DELETE SET NULL,
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

    # Experience entries (1:many per job_profile)
    op.execute("""
    CREATE TABLE IF NOT EXISTS job_profile_experiences (
        id SERIAL PRIMARY KEY,
        job_profile_id INTEGER NOT NULL REFERENCES job_profiles(id) ON DELETE CASCADE,
        source_experience_id INTEGER REFERENCES experiences(id) ON DELETE SET NULL,
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

    # Project entries (1:many per job_profile)
    op.execute("""
    CREATE TABLE IF NOT EXISTS job_profile_projects (
        id SERIAL PRIMARY KEY,
        job_profile_id INTEGER NOT NULL REFERENCES job_profiles(id) ON DELETE CASCADE,
        source_project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
        project_name TEXT NOT NULL,
        description TEXT NOT NULL DEFAULT '',
        start_month_year TEXT,
        end_month_year TEXT,
        reference_links JSONB NOT NULL DEFAULT '[]',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)

    # Research entries (1:many per job_profile)
    op.execute("""
    CREATE TABLE IF NOT EXISTS job_profile_researches (
        id SERIAL PRIMARY KEY,
        job_profile_id INTEGER NOT NULL REFERENCES job_profiles(id) ON DELETE CASCADE,
        source_research_id INTEGER REFERENCES researches(id) ON DELETE SET NULL,
        paper_name TEXT NOT NULL,
        publication_link TEXT NOT NULL,
        description TEXT NOT NULL DEFAULT '',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)

    # Certification entries (1:many per job_profile)
    op.execute("""
    CREATE TABLE IF NOT EXISTS job_profile_certifications (
        id SERIAL PRIMARY KEY,
        job_profile_id INTEGER NOT NULL REFERENCES job_profiles(id) ON DELETE CASCADE,
        source_certification_id INTEGER REFERENCES certifications(id) ON DELETE SET NULL,
        certification_name TEXT NOT NULL,
        verification_link TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)

    # Skill items (1:many per job_profile, replace-all pattern)
    op.execute("""
    CREATE TABLE IF NOT EXISTS job_profile_skill_items (
        id SERIAL PRIMARY KEY,
        job_profile_id INTEGER NOT NULL REFERENCES job_profiles(id) ON DELETE CASCADE,
        kind TEXT NOT NULL CHECK (kind IN ('technical', 'competency')),
        name TEXT NOT NULL,
        sort_order INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)


def downgrade() -> None:
    """Drop all job_profile tables in reverse FK order."""
    op.execute("DROP TABLE IF EXISTS job_profile_skill_items CASCADE")
    op.execute("DROP TABLE IF EXISTS job_profile_certifications CASCADE")
    op.execute("DROP TABLE IF EXISTS job_profile_researches CASCADE")
    op.execute("DROP TABLE IF EXISTS job_profile_projects CASCADE")
    op.execute("DROP TABLE IF EXISTS job_profile_experiences CASCADE")
    op.execute("DROP TABLE IF EXISTS job_profile_educations CASCADE")
    op.execute("DROP TABLE IF EXISTS job_profile_personal_details CASCADE")
    op.execute("DROP TABLE IF EXISTS job_profiles CASCADE")
