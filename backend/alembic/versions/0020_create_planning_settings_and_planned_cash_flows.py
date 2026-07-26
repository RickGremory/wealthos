"""Create planning_settings and planned_cash_flows (SPEC-004).

Revision ID: 0020_create_planning_settings_and_planned_cash_flows
Revises: 0019_create_timeline_events
Create Date: 2026-07-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0020_create_planning_settings_and_planned_cash_flows"
down_revision: str | None = "0019_create_timeline_events"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "planning_settings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("default_horizon", sa.String(length=20), nullable=False),
        sa.Column("safety_reserve_strategy", sa.String(length=30), nullable=False),
        sa.Column("safety_reserve_amount", sa.Numeric(precision=19, scale=4), nullable=True),
        sa.Column("linked_emergency_goal_id", sa.Uuid(), nullable=True),
        sa.Column("include_expected_income", sa.Boolean(), nullable=False),
        sa.Column("include_estimated_expenses", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "safety_reserve_amount IS NULL OR safety_reserve_amount >= 0",
            name="ck_planning_settings_reserve_amount_non_negative",
        ),
        sa.CheckConstraint(
            "default_horizon IN ('today', '7_days', '30_days', '90_days')",
            name="ck_planning_settings_default_horizon",
        ),
        sa.CheckConstraint(
            "safety_reserve_strategy IN "
            "('none', 'fixed_amount', 'linked_goal', 'percentage_of_cash', 'days_of_expenses')",
            name="ck_planning_settings_reserve_strategy",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", name="uq_planning_settings_organization_id"),
    )

    op.create_table(
        "planned_cash_flows",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("direction", sa.String(length=10), nullable=False),
        sa.Column("amount", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("expected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("certainty", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("settled_transaction_id", sa.Uuid(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_planned_cash_flows_amount_positive"),
        sa.CheckConstraint(
            "direction IN ('inflow', 'outflow')",
            name="ck_planned_cash_flows_direction",
        ),
        sa.CheckConstraint(
            "certainty IN ('confirmed', 'expected', 'estimated')",
            name="ck_planned_cash_flows_certainty",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'settled', 'cancelled', 'expired')",
            name="ck_planned_cash_flows_status",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["settled_transaction_id"], ["transactions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_planned_cash_flows_org_currency_expected_at",
        "planned_cash_flows",
        ["organization_id", "currency", "expected_at"],
    )
    op.create_index(
        "ix_planned_cash_flows_org_status",
        "planned_cash_flows",
        ["organization_id", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_planned_cash_flows_org_status", table_name="planned_cash_flows")
    op.drop_index(
        "ix_planned_cash_flows_org_currency_expected_at",
        table_name="planned_cash_flows",
    )
    op.drop_table("planned_cash_flows")
    op.drop_table("planning_settings")
