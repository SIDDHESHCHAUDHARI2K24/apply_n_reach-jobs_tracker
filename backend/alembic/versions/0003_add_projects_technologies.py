"""add_projects_technologies

Revision ID: 0003_projects_technologies
Revises: b2c3d4e5f6a7
Branch Labels: None
Depends On: None

"""
import sqlalchemy as sa
from alembic import op

revision = '0003_projects_technologies'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS technologies JSONB NOT NULL DEFAULT '[]'")


def downgrade():
    op.execute("ALTER TABLE projects DROP COLUMN IF EXISTS technologies")
