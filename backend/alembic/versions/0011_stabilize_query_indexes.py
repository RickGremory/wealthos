"""Partial / covering indexes for Dashboard and Goals hot paths.

Revision ID: 0011_stabilize_query_indexes
Revises: 0010_create_goals
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0011_stabilize_query_indexes"
down_revision: str | None = "0010_create_goals"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Cash-flow / spending: posted income+expense by org + time.
    op.create_index(
        "ix_transactions_org_posted_cashflow_occurred",
        "transactions",
        ["organization_id", "occurred_at"],
        unique=False,
        postgresql_where=sa.text(
            "status = 'posted' AND transaction_type IN ('income', 'expense')"
        ),
    )
    # Avg daily savings / entry joins after filtering transactions.
    op.create_index(
        "ix_transaction_entries_transaction_id_currency",
        "transaction_entries",
        ["transaction_id", "currency"],
        unique=False,
    )
    # Linked-account savings lookbacks.
    op.create_index(
        "ix_transaction_entries_account_id_currency",
        "transaction_entries",
        ["account_id", "currency"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_transaction_entries_account_id_currency",
        table_name="transaction_entries",
    )
    op.drop_index(
        "ix_transaction_entries_transaction_id_currency",
        table_name="transaction_entries",
    )
    op.drop_index(
        "ix_transactions_org_posted_cashflow_occurred",
        table_name="transactions",
    )
