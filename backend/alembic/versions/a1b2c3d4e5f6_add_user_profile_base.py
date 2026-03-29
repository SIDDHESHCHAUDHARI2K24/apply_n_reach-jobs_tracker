"""add_user_profile_base

Revision ID: a1b2c3d4e5f6
Revises: 1e74ccf552b8
Create Date: 2026-03-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '1e74ccf552b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create user_profiles and personal_details tables."""
    op.execute("""
    CREATE TABLE IF NOT EXISTS user_profiles (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)
    op.execute("""
    CREATE TABLE IF NOT EXISTS personal_details (
        id SERIAL PRIMARY KEY,
        profile_id INTEGER NOT NULL UNIQUE REFERENCES user_profiles(id) ON DELETE CASCADE,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        linkedin_url TEXT NOT NULL,
        github_url TEXT,
        portfolio_url TEXT
    )
    """)


def downgrade() -> None:
    """Drop personal_details and user_profiles tables."""
    op.execute("DROP TABLE IF EXISTS personal_details")
    op.execute("DROP TABLE IF EXISTS user_profiles CASCADE")
