"""add email agent runs table

Revision ID: j0j1k2l3m4n5
Revises: 0005_jp_parity_schema_updates
Create Date: 2026-04-30

"""
from alembic import op

revision = "j0j1k2l3m4n5"
down_revision = "0005_jp_parity_schema_updates"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS job_opening_email_agent_runs (
            id                SERIAL PRIMARY KEY,
            opening_id        INTEGER NOT NULL REFERENCES job_openings(id) ON DELETE CASCADE,
            user_id           INTEGER NOT NULL REFERENCES users(id),
            status            TEXT NOT NULL DEFAULT 'running'
                                  CHECK (status IN ('idle', 'running', 'paused', 'succeeded', 'failed')),
            current_node      TEXT,
            state             JSONB,
            events            JSONB NOT NULL DEFAULT '[]'::jsonb,
            error_message     TEXT,
            started_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            completed_at      TIMESTAMPTZ,
            created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_email_agent_runs_opening ON job_opening_email_agent_runs(opening_id)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS job_opening_email_agent_runs")
