"""agent_state_and_extraction_v2

Revision ID: e5f6a7b8c9d0
Revises: a9c2e41fd6b0
Create Date: 2026-04-17
"""
from typing import Sequence, Union
from alembic import op

revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, Sequence[str], None] = 'a9c2e41fd6b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add agent_status and agent_state to job_openings (agent_run_id FK added after table creation)
    op.execute("""
        ALTER TABLE job_openings
            ADD COLUMN agent_status TEXT NOT NULL DEFAULT 'idle'
                CHECK (agent_status IN ('idle', 'running', 'succeeded', 'failed')),
            ADD COLUMN agent_run_id INTEGER,
            ADD COLUMN agent_state JSONB
    """)

    # 2. Create job_opening_agent_runs table
    op.execute("""
        CREATE TABLE job_opening_agent_runs (
            id                SERIAL PRIMARY KEY,
            opening_id        INTEGER NOT NULL REFERENCES job_openings(id) ON DELETE CASCADE,
            user_id           INTEGER NOT NULL REFERENCES users(id),
            status            TEXT NOT NULL DEFAULT 'running'
                                  CHECK (status IN ('running', 'succeeded', 'failed', 'cancelled')),
            current_node      TEXT,
            state             JSONB,
            events            JSONB NOT NULL DEFAULT '[]'::jsonb,
            error_message     TEXT,
            started_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            completed_at      TIMESTAMPTZ,
            created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE INDEX ix_agent_runs_opening ON job_opening_agent_runs(opening_id)
    """)

    # 3. Add FK from job_openings.agent_run_id -> job_opening_agent_runs.id
    op.execute("""
        ALTER TABLE job_openings
            ADD CONSTRAINT fk_job_openings_agent_run_id
                FOREIGN KEY (agent_run_id) REFERENCES job_opening_agent_runs(id)
    """)

    # 4. Add new extraction columns to job_opening_extracted_details_versions
    op.execute("""
        ALTER TABLE job_opening_extracted_details_versions
            ADD COLUMN role_summary TEXT,
            ADD COLUMN technical_keywords JSONB,
            ADD COLUMN sector_keywords JSONB,
            ADD COLUMN business_sectors JSONB,
            ADD COLUMN problem_being_solved TEXT,
            ADD COLUMN useful_experiences JSONB
    """)

    # 5. Add summary column to job_profiles
    op.execute("""
        ALTER TABLE job_profiles
            ADD COLUMN summary TEXT
    """)


def downgrade() -> None:
    # Remove summary from job_profiles
    op.execute("""
        ALTER TABLE job_profiles
            DROP COLUMN IF EXISTS summary
    """)

    # Remove extraction columns from job_opening_extracted_details_versions
    op.execute("""
        ALTER TABLE job_opening_extracted_details_versions
            DROP COLUMN IF EXISTS role_summary,
            DROP COLUMN IF EXISTS technical_keywords,
            DROP COLUMN IF EXISTS sector_keywords,
            DROP COLUMN IF EXISTS business_sectors,
            DROP COLUMN IF EXISTS problem_being_solved,
            DROP COLUMN IF EXISTS useful_experiences
    """)

    # Drop FK constraint before dropping agent_runs table
    op.execute("""
        ALTER TABLE job_openings
            DROP CONSTRAINT IF EXISTS fk_job_openings_agent_run_id
    """)

    # Drop job_opening_agent_runs (index dropped automatically with the table)
    op.execute("""
        DROP TABLE IF EXISTS job_opening_agent_runs
    """)

    # Remove agent columns from job_openings
    op.execute("""
        ALTER TABLE job_openings
            DROP COLUMN IF EXISTS agent_status,
            DROP COLUMN IF EXISTS agent_run_id,
            DROP COLUMN IF EXISTS agent_state
    """)
