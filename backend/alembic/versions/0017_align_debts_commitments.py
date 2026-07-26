"""Align debts table to SPEC-002 Financial Commitments Phase 1.

Revision ID: 0017_align_debts_commitments
Revises: 0016_create_legal_documents
Create Date: 2026-07-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0017_align_debts_commitments"
down_revision: str | None = "0016_create_legal_documents"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index("uq_active_debt_account", table_name="debts")
    op.drop_index("ix_debts_account_id", table_name="debts")
    op.drop_index("ix_debts_organization_id_status", table_name="debts")

    op.execute(
        sa.text("UPDATE debts SET status = 'closed' WHERE status = 'paid_off'")
    )

    op.alter_column(
        "debts",
        "annual_interest_rate",
        new_column_name="interest_rate",
        existing_type=sa.Numeric(9, 4),
        type_=sa.Numeric(9, 6),
        existing_nullable=False,
        nullable=True,
    )
    op.alter_column(
        "debts",
        "minimum_payment",
        existing_type=sa.Numeric(19, 4),
        nullable=True,
    )
    op.alter_column(
        "debts",
        "original_principal",
        new_column_name="original_amount",
        existing_type=sa.Numeric(19, 4),
        existing_nullable=True,
    )
    op.alter_column(
        "debts",
        "payment_day",
        new_column_name="due_day",
        existing_type=sa.SmallInteger(),
        existing_nullable=True,
    )
    op.alter_column(
        "debts",
        "paid_off_at",
        new_column_name="closed_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
    )

    op.add_column("debts", sa.Column("creditor", sa.String(length=120), nullable=True))
    op.add_column(
        "debts",
        sa.Column(
            "priority",
            sa.String(length=10),
            nullable=False,
            server_default="medium",
        ),
    )
    op.add_column(
        "debts",
        sa.Column("scheduled_payment", sa.Numeric(precision=19, scale=4), nullable=True),
    )
    op.add_column(
        "debts",
        sa.Column("credit_limit", sa.Numeric(precision=19, scale=4), nullable=True),
    )
    op.add_column(
        "debts",
        sa.Column(
            "version",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )
    op.drop_column("debts", "opened_at")

    # tax_debt is removed from the domain; map legacy rows to other.
    op.execute(sa.text("UPDATE debts SET debt_type = 'other' WHERE debt_type = 'tax_debt'"))

    op.create_unique_constraint("debts_account_unique_idx", "debts", ["account_id"])
    op.create_index(
        "debts_organization_status_idx",
        "debts",
        ["organization_id", "status"],
    )
    op.create_index(
        "debts_organization_currency_idx",
        "debts",
        ["organization_id", "currency"],
    )
    op.create_index(
        "debts_organization_due_day_idx",
        "debts",
        ["organization_id", "due_day"],
    )
    op.create_index(
        "debts_organization_priority_idx",
        "debts",
        ["organization_id", "priority"],
    )

    op.alter_column("debts", "priority", server_default=None)
    op.alter_column("debts", "version", server_default=None)


def downgrade() -> None:
    op.drop_index("debts_organization_priority_idx", table_name="debts")
    op.drop_index("debts_organization_due_day_idx", table_name="debts")
    op.drop_index("debts_organization_currency_idx", table_name="debts")
    op.drop_index("debts_organization_status_idx", table_name="debts")
    op.drop_constraint("debts_account_unique_idx", "debts", type_="unique")

    op.add_column("debts", sa.Column("opened_at", sa.Date(), nullable=True))
    op.drop_column("debts", "version")
    op.drop_column("debts", "credit_limit")
    op.drop_column("debts", "scheduled_payment")
    op.drop_column("debts", "priority")
    op.drop_column("debts", "creditor")

    op.alter_column(
        "debts",
        "closed_at",
        new_column_name="paid_off_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
    )
    op.alter_column(
        "debts",
        "due_day",
        new_column_name="payment_day",
        existing_type=sa.SmallInteger(),
        existing_nullable=True,
    )
    op.alter_column(
        "debts",
        "original_amount",
        new_column_name="original_principal",
        existing_type=sa.Numeric(19, 4),
        existing_nullable=True,
    )
    op.execute(sa.text("UPDATE debts SET status = 'paid_off' WHERE status = 'closed'"))
    op.execute(
        sa.text(
            "UPDATE debts SET minimum_payment = 0.0001 "
            "WHERE minimum_payment IS NULL"
        )
    )
    op.alter_column(
        "debts",
        "minimum_payment",
        existing_type=sa.Numeric(19, 4),
        nullable=False,
    )
    op.execute(
        sa.text("UPDATE debts SET interest_rate = 0 WHERE interest_rate IS NULL")
    )
    op.alter_column(
        "debts",
        "interest_rate",
        new_column_name="annual_interest_rate",
        existing_type=sa.Numeric(9, 6),
        type_=sa.Numeric(9, 4),
        existing_nullable=True,
        nullable=False,
    )

    op.create_index(
        "ix_debts_organization_id_status",
        "debts",
        ["organization_id", "status"],
    )
    op.create_index("ix_debts_account_id", "debts", ["account_id"])
    op.create_index(
        "uq_active_debt_account",
        "debts",
        ["account_id"],
        unique=True,
        postgresql_where=sa.text(
            "status IN ('active', 'paid_off') AND archived_at IS NULL"
        ),
    )
