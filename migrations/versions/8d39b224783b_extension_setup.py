"""extension_setup

Revision ID: 8d39b224783b
Revises:
Create Date: 2022-11-28 19:17:57.489102

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "8d39b224783b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS pgcrypto;")
