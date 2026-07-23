"""Create accounts table.

Revision ID: 0006_create_accounts
Revises: 0005_user_password_hash
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006_create_accounts"
down_revision: str | None = "0005_user_password_hash"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("account_type", sa.String(length=30), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("opening_balance", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("current_balance", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("institution_name", sa.String(length=120), nullable=True),
        sa.Column("last_four", sa.String(length=4), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_accounts_organization_id", "accounts", ["organization_id"])
    op.create_index(
        "ix_accounts_organization_id_account_type",
        "accounts",
        ["organization_id", "account_type"],
    )
    op.create_index(
        "ix_accounts_organization_id_is_active",
        "accounts",
        ["organization_id", "is_active"],
    )


def downgrade() -> None:
    op.drop_index("ix_accounts_organization_id_is_active", table_name="accounts")
    op.drop_index("ix_accounts_organization_id_account_type", table_name="accounts")
    op.drop_index("ix_accounts_organization_id", table_name="accounts")
    op.drop_table("accounts")
