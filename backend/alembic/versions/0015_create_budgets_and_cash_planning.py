"""Create budgets and cash planning tables.

Revision ID: 0015_create_budgets_and_cash_planning
Revises: 0014_mexico_tax_foundation
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0015_create_budgets_and_cash_planning"
down_revision: str | None = "0014_mexico_tax_foundation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # alembic_version.version_num defaults to VARCHAR(32); this revision id is longer.
    op.execute(sa.text("ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(64)"))

    op.create_table(
        "budgets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("period_type", sa.String(length=20), nullable=False),
        sa.Column("date_from", sa.Date(), nullable=False),
        sa.Column("date_to", sa.Date(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("rollover_policy", sa.String(length=20), nullable=False),
        sa.Column("forecast_method", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("date_from <= date_to", name="ck_budgets_date_range"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_budgets_organization_id_status_date_from_date_to",
        "budgets",
        ["organization_id", "status", "date_from", "date_to"],
    )

    op.create_table(
        "budget_allocations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("budget_id", sa.Uuid(), nullable=False),
        sa.Column("allocation_type", sa.String(length=30), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=True),
        sa.Column("goal_id", sa.Uuid(), nullable=True),
        sa.Column("debt_id", sa.Uuid(), nullable=True),
        sa.Column("tax_profile_id", sa.Uuid(), nullable=True),
        sa.Column("destination_account_id", sa.Uuid(), nullable=True),
        sa.Column("amount", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_budget_allocations_amount_positive"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["budget_id"], ["budgets.id"]),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"]),
        sa.ForeignKeyConstraint(["debt_id"], ["debts.id"]),
        sa.ForeignKeyConstraint(["tax_profile_id"], ["tax_profiles.id"]),
        sa.ForeignKeyConstraint(["destination_account_id"], ["accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "budget_id",
            "allocation_type",
            "category_id",
            "goal_id",
            "debt_id",
            "tax_profile_id",
            name="uq_budget_allocations_type_refs",
        ),
    )
    op.create_index(
        "ix_budget_allocations_budget_id_allocation_type",
        "budget_allocations",
        ["budget_id", "allocation_type"],
    )
    op.create_index(
        "ix_budget_allocations_category_id",
        "budget_allocations",
        ["category_id"],
    )

    op.create_table(
        "budget_allocation_matches",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("budget_allocation_id", sa.Uuid(), nullable=False),
        sa.Column("transaction_id", sa.Uuid(), nullable=False),
        sa.Column("matched_amount", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "matched_amount > 0",
            name="ck_budget_allocation_matches_amount_positive",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["budget_allocation_id"], ["budget_allocations.id"]),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "budget_allocation_id",
            "transaction_id",
            name="uq_budget_allocation_matches_allocation_tx",
        ),
    )
    op.create_index(
        "ix_budget_allocation_matches_budget_allocation_id",
        "budget_allocation_matches",
        ["budget_allocation_id"],
    )
    op.create_index(
        "ix_budget_allocation_matches_transaction_id",
        "budget_allocation_matches",
        ["transaction_id"],
    )

    op.create_table(
        "cash_plans",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("date_from", sa.Date(), nullable=False),
        sa.Column("date_to", sa.Date(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("opening_balance_mode", sa.String(length=30), nullable=False),
        sa.Column(
            "manual_opening_balance",
            sa.Numeric(precision=19, scale=4),
            nullable=True,
        ),
        sa.Column("minimum_cash_buffer_type", sa.String(length=40), nullable=False),
        sa.Column(
            "minimum_cash_buffer_value",
            sa.Numeric(precision=19, scale=4),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("date_from <= date_to", name="ck_cash_plans_date_range"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_cash_plans_organization_id_status_date_from_date_to",
        "cash_plans",
        ["organization_id", "status", "date_from", "date_to"],
    )

    op.create_table(
        "cash_plan_accounts",
        sa.Column("cash_plan_id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["cash_plan_id"], ["cash_plans.id"]),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.PrimaryKeyConstraint("cash_plan_id", "account_id"),
    )
    op.create_index(
        "ix_cash_plan_accounts_account_id",
        "cash_plan_accounts",
        ["account_id"],
    )

    op.create_table(
        "cash_plan_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("cash_plan_id", sa.Uuid(), nullable=False),
        sa.Column("item_type", sa.String(length=20), nullable=False),
        sa.Column("description", sa.String(length=200), nullable=False),
        sa.Column("expected_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("probability", sa.Numeric(precision=9, scale=4), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=True),
        sa.Column("account_id", sa.Uuid(), nullable=True),
        sa.Column("linked_entity_type", sa.String(length=30), nullable=True),
        sa.Column("linked_entity_id", sa.Uuid(), nullable=True),
        sa.Column("recurrence_rule", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("amount > 0", name="ck_cash_plan_items_amount_positive"),
        sa.CheckConstraint(
            "probability >= 0 AND probability <= 100",
            name="ck_cash_plan_items_probability_range",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["cash_plan_id"], ["cash_plans.id"]),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_cash_plan_items_cash_plan_id_expected_date_status",
        "cash_plan_items",
        ["cash_plan_id", "expected_date", "status"],
    )
    op.create_index(
        "ix_cash_plan_items_linked_entity_type_linked_entity_id",
        "cash_plan_items",
        ["linked_entity_type", "linked_entity_id"],
    )

    op.create_table(
        "cash_plan_item_matches",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("cash_plan_item_id", sa.Uuid(), nullable=False),
        sa.Column("transaction_id", sa.Uuid(), nullable=False),
        sa.Column("matched_amount", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "matched_amount > 0",
            name="ck_cash_plan_item_matches_amount_positive",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["cash_plan_item_id"], ["cash_plan_items.id"]),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "cash_plan_item_id",
            "transaction_id",
            name="uq_cash_plan_item_matches_item_tx",
        ),
    )
    op.create_index(
        "ix_cash_plan_item_matches_cash_plan_item_id",
        "cash_plan_item_matches",
        ["cash_plan_item_id"],
    )
    op.create_index(
        "ix_cash_plan_item_matches_transaction_id",
        "cash_plan_item_matches",
        ["transaction_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cash_plan_item_matches_transaction_id",
        table_name="cash_plan_item_matches",
    )
    op.drop_index(
        "ix_cash_plan_item_matches_cash_plan_item_id",
        table_name="cash_plan_item_matches",
    )
    op.drop_table("cash_plan_item_matches")

    op.drop_index(
        "ix_cash_plan_items_linked_entity_type_linked_entity_id",
        table_name="cash_plan_items",
    )
    op.drop_index(
        "ix_cash_plan_items_cash_plan_id_expected_date_status",
        table_name="cash_plan_items",
    )
    op.drop_table("cash_plan_items")

    op.drop_index("ix_cash_plan_accounts_account_id", table_name="cash_plan_accounts")
    op.drop_table("cash_plan_accounts")

    op.drop_index(
        "ix_cash_plans_organization_id_status_date_from_date_to",
        table_name="cash_plans",
    )
    op.drop_table("cash_plans")

    op.drop_index(
        "ix_budget_allocation_matches_transaction_id",
        table_name="budget_allocation_matches",
    )
    op.drop_index(
        "ix_budget_allocation_matches_budget_allocation_id",
        table_name="budget_allocation_matches",
    )
    op.drop_table("budget_allocation_matches")

    op.drop_index("ix_budget_allocations_category_id", table_name="budget_allocations")
    op.drop_index(
        "ix_budget_allocations_budget_id_allocation_type",
        table_name="budget_allocations",
    )
    op.drop_table("budget_allocations")

    op.drop_index(
        "ix_budgets_organization_id_status_date_from_date_to",
        table_name="budgets",
    )
    op.drop_table("budgets")
