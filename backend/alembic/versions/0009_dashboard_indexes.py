"""Add account classification and dashboard indexes.

Revision ID: 0009_dashboard_indexes
Revises: 0008_create_transactions
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009_dashboard_indexes"
down_revision: str | None = "0008_create_transactions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "accounts",
        sa.Column("classification", sa.String(length=20), nullable=True),
    )
    op.execute(
        """
        UPDATE accounts
        SET classification = CASE
            WHEN account_type IN ('credit_card', 'loan') THEN 'liability'
            ELSE 'asset'
        END
        """
    )
    op.alter_column("accounts", "classification", nullable=False)

    op.create_index(
        "ix_accounts_organization_id_is_active_currency",
        "accounts",
        ["organization_id", "is_active", "currency"],
    )
    op.create_index(
        "ix_accounts_organization_id_classification",
        "accounts",
        ["organization_id", "classification"],
    )
    op.create_index(
        "ix_transactions_organization_id_status_occurred_at",
        "transactions",
        ["organization_id", "status", "occurred_at"],
    )
    op.create_index(
        "ix_transactions_organization_id_type_occurred_at",
        "transactions",
        ["organization_id", "transaction_type", "occurred_at"],
    )
    op.create_index(
        "ix_transactions_organization_id_occurred_created",
        "transactions",
        ["organization_id", "occurred_at", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_transactions_organization_id_occurred_created",
        table_name="transactions",
    )
    op.drop_index(
        "ix_transactions_organization_id_type_occurred_at",
        table_name="transactions",
    )
    op.drop_index(
        "ix_transactions_organization_id_status_occurred_at",
        table_name="transactions",
    )
    op.drop_index(
        "ix_accounts_organization_id_classification",
        table_name="accounts",
    )
    op.drop_index(
        "ix_accounts_organization_id_is_active_currency",
        table_name="accounts",
    )
    op.drop_column("accounts", "classification")
