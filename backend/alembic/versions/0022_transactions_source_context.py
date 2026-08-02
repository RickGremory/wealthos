"""Alembic migration: transaction source context for Recurring confirm (SPEC-005 PR5).

Revision ID: 0022_transactions_source_context
Revises: 0021_create_recurring_engine
Create Date: 2026-08-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0022_transactions_source_context"
down_revision: str | None = "0021_create_recurring_engine"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "transactions",
        sa.Column("source_type", sa.String(length=40), nullable=True),
    )
    op.add_column(
        "transactions",
        sa.Column("source_occurrence_key", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "transactions",
        sa.Column("related_resource_type", sa.String(length=40), nullable=True),
    )
    op.add_column(
        "transactions",
        sa.Column("related_resource_id", sa.Uuid(), nullable=True),
    )
    op.create_index(
        "ix_transactions_organization_id_source_occurrence_key",
        "transactions",
        ["organization_id", "source_occurrence_key"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_transactions_organization_id_source_occurrence_key",
        table_name="transactions",
    )
    op.drop_column("transactions", "related_resource_id")
    op.drop_column("transactions", "related_resource_type")
    op.drop_column("transactions", "source_occurrence_key")
    op.drop_column("transactions", "source_type")
