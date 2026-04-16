"""job_tracker_foundation_schema

Revision ID: b81c3184eb7c
Revises: d4e5f6a7b8c9
Create Date: 2026-04-16 18:24:23.230625

Creates all job_tracker tables:
- job_openings
- job_opening_status_history
- job_opening_extraction_runs
- job_opening_extracted_details_versions
- job_opening_resumes
- job_opening_personal
- job_opening_education
- job_opening_experience
- job_opening_projects
- job_opening_research
- job_opening_certifications
- job_opening_skills
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b81c3184eb7c'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all job_tracker tables."""
    op.execute("""
    CREATE TABLE job_openings (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        job_profile_id INTEGER REFERENCES job_profiles(id) ON DELETE SET NULL,
        source_url TEXT,
        company_name TEXT NOT NULL,
        role_name TEXT NOT NULL,
        current_status TEXT NOT NULL DEFAULT 'Interested' CHECK (current_status IN ('Interested','Applied','Interviewing','Offer','Withdrawn','Rejected')),
        notes TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)
    op.execute("CREATE INDEX ix_job_openings_user_id ON job_openings(user_id)")
    op.execute("CREATE INDEX ix_job_openings_current_status ON job_openings(current_status)")
    op.execute("CREATE INDEX ix_job_openings_created_at ON job_openings(created_at)")

    op.execute("""
    CREATE TABLE job_opening_status_history (
        id SERIAL PRIMARY KEY,
        opening_id INTEGER NOT NULL REFERENCES job_openings(id) ON DELETE CASCADE,
        from_status TEXT,
        to_status TEXT NOT NULL,
        changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        changed_by_user_id INTEGER NOT NULL REFERENCES users(id)
    )
    """)
    op.execute("CREATE INDEX ix_status_history_opening_id ON job_opening_status_history(opening_id)")

    op.execute("""
    CREATE TABLE job_opening_extraction_runs (
        id SERIAL PRIMARY KEY,
        opening_id INTEGER NOT NULL REFERENCES job_openings(id) ON DELETE CASCADE,
        status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','running','succeeded','failed')),
        attempt_number INTEGER NOT NULL DEFAULT 1,
        started_at TIMESTAMPTZ,
        completed_at TIMESTAMPTZ,
        next_retry_at TIMESTAMPTZ,
        error_message TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)
    op.execute("CREATE INDEX ix_extraction_runs_opening_id_status ON job_opening_extraction_runs(opening_id, status)")

    op.execute("""
    CREATE TABLE job_opening_extracted_details_versions (
        id SERIAL PRIMARY KEY,
        run_id INTEGER NOT NULL REFERENCES job_opening_extraction_runs(id) ON DELETE CASCADE,
        opening_id INTEGER NOT NULL REFERENCES job_openings(id) ON DELETE CASCADE,
        schema_version INTEGER NOT NULL DEFAULT 1,
        job_title TEXT,
        company_name TEXT,
        location TEXT,
        employment_type TEXT,
        salary_range TEXT,
        description_summary TEXT,
        required_skills JSONB,
        preferred_skills JSONB,
        experience_level TEXT,
        posted_date TEXT,
        application_deadline TEXT,
        extracted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        raw_payload JSONB,
        extractor_model TEXT,
        source_url TEXT
    )
    """)
    op.execute("CREATE INDEX ix_extracted_details_opening_id ON job_opening_extracted_details_versions(opening_id)")

    op.execute("""
    CREATE TABLE job_opening_resumes (
        id SERIAL PRIMARY KEY,
        opening_id INTEGER NOT NULL REFERENCES job_openings(id) ON DELETE CASCADE UNIQUE,
        source_job_profile_id INTEGER REFERENCES job_profiles(id) ON DELETE SET NULL,
        snapshot_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        snapshot_version INTEGER NOT NULL DEFAULT 1,
        source_section_count INTEGER NOT NULL DEFAULT 7  -- 7 resume sections: personal, education, experience, projects, research, certifications, skills; set by service layer at snapshot time
    )
    """)

    op.execute("""
    CREATE TABLE job_opening_personal (
        id SERIAL PRIMARY KEY,
        resume_id INTEGER NOT NULL REFERENCES job_opening_resumes(id) ON DELETE CASCADE UNIQUE,
        full_name TEXT,
        email TEXT,
        phone TEXT,
        location TEXT,
        linkedin_url TEXT,
        github_url TEXT,
        portfolio_url TEXT,
        summary TEXT
    )
    """)

    op.execute("""
    CREATE TABLE job_opening_education (
        id SERIAL PRIMARY KEY,
        resume_id INTEGER NOT NULL REFERENCES job_opening_resumes(id) ON DELETE CASCADE,
        institution TEXT NOT NULL,
        degree TEXT,
        field_of_study TEXT,
        start_date TEXT,
        end_date TEXT,
        grade TEXT,
        description TEXT,
        display_order INTEGER NOT NULL DEFAULT 0
    )
    """)

    op.execute("""
    CREATE TABLE job_opening_experience (
        id SERIAL PRIMARY KEY,
        resume_id INTEGER NOT NULL REFERENCES job_opening_resumes(id) ON DELETE CASCADE,
        company TEXT NOT NULL,
        title TEXT NOT NULL,
        location TEXT,
        start_date TEXT,
        end_date TEXT,
        is_current BOOLEAN NOT NULL DEFAULT FALSE,
        description TEXT,
        display_order INTEGER NOT NULL DEFAULT 0
    )
    """)

    op.execute("""
    CREATE TABLE job_opening_projects (
        id SERIAL PRIMARY KEY,
        resume_id INTEGER NOT NULL REFERENCES job_opening_resumes(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        description TEXT,
        url TEXT,
        start_date TEXT,
        end_date TEXT,
        technologies JSONB,
        display_order INTEGER NOT NULL DEFAULT 0
    )
    """)

    op.execute("""
    CREATE TABLE job_opening_research (
        id SERIAL PRIMARY KEY,
        resume_id INTEGER NOT NULL REFERENCES job_opening_resumes(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        publication TEXT,
        published_date TEXT,
        url TEXT,
        description TEXT,
        display_order INTEGER NOT NULL DEFAULT 0
    )
    """)

    op.execute("""
    CREATE TABLE job_opening_certifications (
        id SERIAL PRIMARY KEY,
        resume_id INTEGER NOT NULL REFERENCES job_opening_resumes(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        issuer TEXT,
        issue_date TEXT,
        expiry_date TEXT,
        credential_id TEXT,
        url TEXT,
        display_order INTEGER NOT NULL DEFAULT 0
    )
    """)

    op.execute("""
    CREATE TABLE job_opening_skills (
        id SERIAL PRIMARY KEY,
        resume_id INTEGER NOT NULL REFERENCES job_opening_resumes(id) ON DELETE CASCADE,
        category TEXT NOT NULL,
        name TEXT NOT NULL,
        proficiency_level TEXT,
        display_order INTEGER NOT NULL DEFAULT 0
    )
    """)


def downgrade() -> None:
    """Drop all job_tracker tables in reverse FK order."""
    op.execute("DROP TABLE IF EXISTS job_opening_skills CASCADE")
    op.execute("DROP TABLE IF EXISTS job_opening_certifications CASCADE")
    op.execute("DROP TABLE IF EXISTS job_opening_research CASCADE")
    op.execute("DROP TABLE IF EXISTS job_opening_projects CASCADE")
    op.execute("DROP TABLE IF EXISTS job_opening_experience CASCADE")
    op.execute("DROP TABLE IF EXISTS job_opening_education CASCADE")
    op.execute("DROP TABLE IF EXISTS job_opening_personal CASCADE")
    op.execute("DROP TABLE IF EXISTS job_opening_resumes CASCADE")
    op.execute("DROP TABLE IF EXISTS job_opening_extracted_details_versions CASCADE")
    op.execute("DROP TABLE IF EXISTS job_opening_extraction_runs CASCADE")
    op.execute("DROP TABLE IF EXISTS job_opening_status_history CASCADE")
    op.execute("DROP TABLE IF EXISTS job_openings CASCADE")
