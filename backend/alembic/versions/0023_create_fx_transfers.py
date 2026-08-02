"""Alembic migration: foreign-exchange transfers (Sprint 9.6).

Revision ID: 0023_create_fx_transfers
Revises: 0022_transactions_source_context
Create Date: 2026-08-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0023_create_fx_transfers"
down_revision: str | None = "0022_transactions_source_context"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "fx_transfers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("source_account_id", sa.Uuid(), nullable=False),
        sa.Column("destination_account_id", sa.Uuid(), nullable=False),
        sa.Column("source_amount", sa.Numeric(18, 4), nullable=False),
        sa.Column("source_currency", sa.String(length=3), nullable=False),
        sa.Column("destination_amount", sa.Numeric(18, 4), nullable=False),
        sa.Column("destination_currency", sa.String(length=3), nullable=False),
        sa.Column("effective_exchange_rate", sa.Numeric(24, 10), nullable=False),
        sa.Column("fee_amount", sa.Numeric(18, 4), nullable=True),
        sa.Column("fee_currency", sa.String(length=3), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("description", sa.String(length=200), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("source_transaction_id", sa.Uuid(), nullable=False),
        sa.Column("destination_transaction_id", sa.Uuid(), nullable=False),
        sa.Column("fee_transaction_id", sa.Uuid(), nullable=True),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["source_account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["destination_account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["source_transaction_id"], ["transactions.id"]),
        sa.ForeignKeyConstraint(["destination_transaction_id"], ["transactions.id"]),
        sa.ForeignKeyConstraint(["fee_transaction_id"], ["transactions.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "source_account_id <> destination_account_id",
            name="ck_fx_transfers_distinct_accounts",
        ),
        sa.CheckConstraint(
            "source_currency <> destination_currency",
            name="ck_fx_transfers_distinct_currencies",
        ),
        sa.CheckConstraint("source_amount > 0", name="ck_fx_transfers_source_amount_pos"),
        sa.CheckConstraint(
            "destination_amount > 0",
            name="ck_fx_transfers_destination_amount_pos",
        ),
        sa.CheckConstraint(
            "effective_exchange_rate > 0",
            name="ck_fx_transfers_rate_pos",
        ),
    )
    op.create_index(
        "ix_fx_transfers_organization_id",
        "fx_transfers",
        ["organization_id"],
    )
    op.create_index(
        "ix_fx_transfers_organization_id_occurred_at",
        "fx_transfers",
        ["organization_id", "occurred_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_fx_transfers_organization_id_occurred_at",
        table_name="fx_transfers",
    )
    op.drop_index("ix_fx_transfers_organization_id", table_name="fx_transfers")
    op.drop_table("fx_transfers")
