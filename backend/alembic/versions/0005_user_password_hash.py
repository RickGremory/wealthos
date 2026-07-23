"""Add user password_hash column.

Revision ID: 0005_user_password_hash
Revises: 0004_users_memberships
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_user_password_hash"
down_revision: str | None = "0004_users_memberships"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Dev-friendly reset: existing bootstrap users have no credentials.
    op.execute("TRUNCATE TABLE organization_memberships, organizations, users CASCADE")
    op.add_column(
        "users",
        sa.Column("password_hash", sa.String(length=255), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("users", "password_hash")
