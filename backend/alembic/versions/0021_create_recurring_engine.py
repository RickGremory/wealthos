"""Alembic migration: Recurring Engine tables (SPEC-005 PR1).

Revision ID: 0021_create_recurring_engine
Revises: 0020_create_planning_settings_and_planned_cash_flows
Create Date: 2026-08-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0021_create_recurring_engine"
down_revision: str | None = "0020_create_planning_settings_and_planned_cash_flows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    op.create_table(
        "recurring_rules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("source_type", sa.String(length=20), nullable=False),
        sa.Column("related_resource_type", sa.String(length=40), nullable=True),
        sa.Column("related_resource_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "source_type IN "
            "('manual', 'commitment', 'goal', 'tax', 'system', 'imported')",
            name="ck_recurring_rules_source_type",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'paused', 'ended', 'archived')",
            name="ck_recurring_rules_status",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_recurring_rules_org_status",
        "recurring_rules",
        ["organization_id", "status"],
    )

    op.create_table(
        "recurring_rule_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("recurring_rule_id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_until", sa.Date(), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("direction", sa.String(length=10), nullable=False),
        sa.Column("amount", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("amount_strategy", sa.String(length=20), nullable=False),
        sa.Column("certainty", sa.String(length=20), nullable=False),
        sa.Column("settlement_mode", sa.String(length=30), nullable=False),
        sa.Column("frequency", sa.String(length=10), nullable=False),
        sa.Column("interval", sa.Integer(), nullable=False),
        sa.Column("days_of_week", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("day_of_month", sa.SmallInteger(), nullable=True),
        sa.Column("month_of_year", sa.SmallInteger(), nullable=True),
        sa.Column("end_of_month", sa.Boolean(), nullable=False),
        sa.Column("invalid_date_policy", sa.String(length=30), nullable=False),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("ends_on", sa.Date(), nullable=True),
        sa.Column("grace_period_days", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=True),
        sa.Column("destination_account_id", sa.Uuid(), nullable=True),
        sa.Column("category_id", sa.Uuid(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_recurring_versions_amount_positive"),
        sa.CheckConstraint("interval >= 1", name="ck_recurring_versions_interval"),
        sa.CheckConstraint(
            "grace_period_days >= 0",
            name="ck_recurring_versions_grace",
        ),
        sa.CheckConstraint(
            "effective_until IS NULL OR effective_until >= effective_from",
            name="ck_recurring_versions_effective_range",
        ),
        sa.CheckConstraint(
            "ends_on IS NULL OR ends_on >= starts_on",
            name="ck_recurring_versions_starts_ends",
        ),
        sa.CheckConstraint(
            "direction IN ('inflow', 'outflow', 'transfer')",
            name="ck_recurring_versions_direction",
        ),
        sa.CheckConstraint(
            "amount_strategy IN ('fixed', 'estimated')",
            name="ck_recurring_versions_amount_strategy",
        ),
        sa.CheckConstraint(
            "certainty IN ('confirmed', 'expected', 'estimated')",
            name="ck_recurring_versions_certainty",
        ),
        sa.CheckConstraint(
            "settlement_mode IN ('single_transaction', 'cumulative')",
            name="ck_recurring_versions_settlement_mode",
        ),
        sa.CheckConstraint(
            "frequency IN ('daily', 'weekly', 'monthly', 'yearly')",
            name="ck_recurring_versions_frequency",
        ),
        sa.CheckConstraint(
            "invalid_date_policy IN ('last_day_of_month', 'skip_occurrence')",
            name="ck_recurring_versions_invalid_date_policy",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(
            ["recurring_rule_id"],
            ["recurring_rules.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_recurring_versions_rule_effective",
        "recurring_rule_versions",
        ["recurring_rule_id", "effective_from", "effective_until"],
    )
    op.create_index(
        "ix_recurring_versions_org_currency",
        "recurring_rule_versions",
        ["organization_id", "currency"],
    )
    # Non-overlapping effective periods per rule (inclusive daterange).
    op.execute(
        """
        ALTER TABLE recurring_rule_versions
        ADD CONSTRAINT ex_recurring_versions_no_overlap
        EXCLUDE USING gist (
            recurring_rule_id WITH =,
            daterange(
                effective_from,
                COALESCE(effective_until, 'infinity'::date),
                '[]'
            ) WITH &&
        )
        """
    )

    op.create_table(
        "recurring_rule_pauses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("recurring_rule_id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("ends_on", sa.Date(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "ends_on IS NULL OR ends_on >= starts_on",
            name="ck_recurring_pauses_range",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(
            ["recurring_rule_id"],
            ["recurring_rules.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_recurring_pauses_rule_dates",
        "recurring_rule_pauses",
        ["recurring_rule_id", "starts_on", "ends_on"],
    )

    op.create_table(
        "recurring_occurrence_exceptions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("recurring_rule_id", sa.Uuid(), nullable=False),
        sa.Column("original_occurrence_key", sa.String(length=120), nullable=False),
        sa.Column("original_expected_on", sa.Date(), nullable=False),
        sa.Column("exception_type", sa.String(length=30), nullable=False),
        sa.Column("replacement_expected_on", sa.Date(), nullable=True),
        sa.Column("replacement_amount", sa.Numeric(precision=19, scale=4), nullable=True),
        sa.Column("replacement_certainty", sa.String(length=20), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "exception_type IN ('skip', 'reschedule', 'amount_override', 'override')",
            name="ck_recurring_exceptions_type",
        ),
        sa.CheckConstraint(
            "replacement_amount IS NULL OR replacement_amount > 0",
            name="ck_recurring_exceptions_amount",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(
            ["recurring_rule_id"],
            ["recurring_rules.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_recurring_exceptions_rule_original_date",
        "recurring_occurrence_exceptions",
        ["recurring_rule_id", "original_expected_on"],
    )
    op.create_index(
        "ix_recurring_exceptions_replacement_date",
        "recurring_occurrence_exceptions",
        ["recurring_rule_id", "replacement_expected_on"],
    )
    op.execute(
        """
        CREATE UNIQUE INDEX uq_recurring_exceptions_active_key
        ON recurring_occurrence_exceptions (recurring_rule_id, original_occurrence_key)
        WHERE is_active = true
        """
    )

    op.create_table(
        "recurring_occurrence_settlements",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("recurring_rule_id", sa.Uuid(), nullable=False),
        sa.Column("occurrence_key", sa.String(length=120), nullable=False),
        sa.Column("transaction_id", sa.Uuid(), nullable=False),
        sa.Column("settled_amount", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("link_type", sa.String(length=30), nullable=False),
        sa.Column("linked_by", sa.Uuid(), nullable=True),
        sa.Column("linked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("voided_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "settled_amount > 0",
            name="ck_recurring_settlements_amount",
        ),
        sa.CheckConstraint(
            "link_type IN ('explicit', 'manual', 'suggested_confirmed')",
            name="ck_recurring_settlements_link_type",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(
            ["recurring_rule_id"],
            ["recurring_rules.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "occurrence_key",
            "transaction_id",
            name="uq_recurring_settlements_occurrence_transaction",
        ),
    )
    op.create_index(
        "ix_recurring_settlements_occurrence",
        "recurring_occurrence_settlements",
        ["organization_id", "occurrence_key"],
    )
    op.create_index(
        "ix_recurring_settlements_transaction",
        "recurring_occurrence_settlements",
        ["transaction_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_recurring_settlements_transaction",
        table_name="recurring_occurrence_settlements",
    )
    op.drop_index(
        "ix_recurring_settlements_occurrence",
        table_name="recurring_occurrence_settlements",
    )
    op.drop_table("recurring_occurrence_settlements")

    op.execute("DROP INDEX IF EXISTS uq_recurring_exceptions_active_key")
    op.drop_index(
        "ix_recurring_exceptions_replacement_date",
        table_name="recurring_occurrence_exceptions",
    )
    op.drop_index(
        "ix_recurring_exceptions_rule_original_date",
        table_name="recurring_occurrence_exceptions",
    )
    op.drop_table("recurring_occurrence_exceptions")

    op.drop_index("ix_recurring_pauses_rule_dates", table_name="recurring_rule_pauses")
    op.drop_table("recurring_rule_pauses")

    op.execute(
        "ALTER TABLE recurring_rule_versions "
        "DROP CONSTRAINT IF EXISTS ex_recurring_versions_no_overlap"
    )
    op.drop_index(
        "ix_recurring_versions_org_currency",
        table_name="recurring_rule_versions",
    )
    op.drop_index(
        "ix_recurring_versions_rule_effective",
        table_name="recurring_rule_versions",
    )
    op.drop_table("recurring_rule_versions")

    op.drop_index("ix_recurring_rules_org_status", table_name="recurring_rules")
    op.drop_table("recurring_rules")
