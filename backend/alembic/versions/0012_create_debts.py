"""Create debts and debt_payments tables.

Revision ID: 0012_create_debts
Revises: 0011_stabilize_query_indexes
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0012_create_debts"
down_revision: str | None = "0011_stabilize_query_indexes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "debts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("debt_type", sa.String(length=30), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("annual_interest_rate", sa.Numeric(precision=9, scale=4), nullable=False),
        sa.Column("minimum_payment", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("original_principal", sa.Numeric(precision=19, scale=4), nullable=True),
        sa.Column("opened_at", sa.Date(), nullable=True),
        sa.Column("maturity_date", sa.Date(), nullable=True),
        sa.Column("payment_day", sa.SmallInteger(), nullable=True),
        sa.Column("statement_day", sa.SmallInteger(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("paid_off_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_debts_organization_id_status",
        "debts",
        ["organization_id", "status"],
    )
    op.create_index(
        "ix_debts_organization_id_debt_type",
        "debts",
        ["organization_id", "debt_type"],
    )
    op.create_index("ix_debts_account_id", "debts", ["account_id"])
    op.create_index(
        "uq_active_debt_account",
        "debts",
        ["account_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('active', 'paid_off') AND archived_at IS NULL"),
    )

    op.create_table(
        "debt_payments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("debt_id", sa.Uuid(), nullable=False),
        sa.Column("transaction_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("principal_amount", sa.Numeric(precision=19, scale=4), nullable=True),
        sa.Column("interest_amount", sa.Numeric(precision=19, scale=4), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["debt_id"], ["debts.id"]),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_debt_payments_organization_id_debt_id_paid_at",
        "debt_payments",
        ["organization_id", "debt_id", "paid_at"],
    )
    op.create_index(
        "uq_debt_payments_transaction_id",
        "debt_payments",
        ["transaction_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "uq_debt_payments_transaction_id",
        table_name="debt_payments",
    )
    op.drop_index(
        "ix_debt_payments_organization_id_debt_id_paid_at",
        table_name="debt_payments",
    )
    op.drop_table("debt_payments")
    op.drop_index("uq_active_debt_account", table_name="debts")
    op.drop_index("ix_debts_account_id", table_name="debts")
    op.drop_index("ix_debts_organization_id_debt_type", table_name="debts")
    op.drop_index("ix_debts_organization_id_status", table_name="debts")
    op.drop_table("debts")
