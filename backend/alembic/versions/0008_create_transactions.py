"""Create transactions and transaction_entries tables.

Revision ID: 0008_create_transactions
Revises: 0007_create_categories
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008_create_transactions"
down_revision: str | None = "0007_create_categories"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "transactions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("transaction_type", sa.String(length=20), nullable=False),
        sa.Column("description", sa.String(length=200), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("updated_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("voided_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("voided_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["voided_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transactions_organization_id", "transactions", ["organization_id"])
    op.create_index(
        "ix_transactions_organization_id_occurred_at",
        "transactions",
        ["organization_id", "occurred_at"],
    )
    op.create_index(
        "ix_transactions_organization_id_transaction_type",
        "transactions",
        ["organization_id", "transaction_type"],
    )
    op.create_index(
        "ix_transactions_organization_id_status",
        "transactions",
        ["organization_id", "status"],
    )
    op.create_index(
        "ix_transactions_organization_id_category_id",
        "transactions",
        ["organization_id", "category_id"],
    )

    op.create_table(
        "transaction_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("transaction_id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(
            ["transaction_id"],
            ["transactions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_transaction_entries_transaction_id",
        "transaction_entries",
        ["transaction_id"],
    )
    op.create_index(
        "ix_transaction_entries_account_id",
        "transaction_entries",
        ["account_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_transaction_entries_account_id", table_name="transaction_entries")
    op.drop_index(
        "ix_transaction_entries_transaction_id",
        table_name="transaction_entries",
    )
    op.drop_table("transaction_entries")
    op.drop_index(
        "ix_transactions_organization_id_category_id",
        table_name="transactions",
    )
    op.drop_index("ix_transactions_organization_id_status", table_name="transactions")
    op.drop_index(
        "ix_transactions_organization_id_transaction_type",
        table_name="transactions",
    )
    op.drop_index(
        "ix_transactions_organization_id_occurred_at",
        table_name="transactions",
    )
    op.drop_index("ix_transactions_organization_id", table_name="transactions")
    op.drop_table("transactions")
