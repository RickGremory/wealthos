"""Create tax foundation tables.

Revision ID: 0013_create_tax_foundation
Revises: 0012_create_debts
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0013_create_tax_foundation"
down_revision: str | None = "0012_create_debts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tax_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=False),
        sa.Column("jurisdiction", sa.String(length=120), nullable=True),
        sa.Column("taxpayer_type", sa.String(length=30), nullable=False),
        sa.Column("tax_regime", sa.String(length=120), nullable=True),
        sa.Column("filing_frequency", sa.String(length=20), nullable=False),
        sa.Column("fiscal_year_start_month", sa.SmallInteger(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("reserve_account_id", sa.Uuid(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["reserve_account_id"], ["accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_tax_profiles_organization_id_is_active",
        "tax_profiles",
        ["organization_id", "is_active"],
    )
    op.create_index(
        "uq_tax_profiles_active_organization",
        "tax_profiles",
        ["organization_id"],
        unique=True,
        postgresql_where=sa.text("is_active IS TRUE"),
    )

    op.create_table(
        "tax_rules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("tax_profile_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("tax_type", sa.String(length=40), nullable=False),
        sa.Column("calculation_method", sa.String(length=20), nullable=False),
        sa.Column("rate", sa.Numeric(precision=9, scale=4), nullable=True),
        sa.Column("fixed_amount", sa.Numeric(precision=19, scale=4), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("applies_to", sa.String(length=40), nullable=False),
        sa.Column("tax_inclusion_mode", sa.String(length=20), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["tax_profile_id"], ["tax_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_tax_rules_profile_active_effective",
        "tax_rules",
        ["tax_profile_id", "is_active", "effective_from", "effective_to"],
    )

    op.create_table(
        "tax_rule_categories",
        sa.Column("tax_rule_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["tax_rule_id"], ["tax_rules.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tax_rule_id", "category_id"),
        sa.UniqueConstraint("tax_rule_id", "category_id", name="uq_tax_rule_category"),
    )

    op.create_table(
        "tax_category_mappings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("tax_profile_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("tax_treatment", sa.String(length=40), nullable=False),
        sa.Column("deductibility_percentage", sa.Numeric(precision=9, scale=4), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["tax_profile_id"], ["tax_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tax_profile_id",
            "category_id",
            name="uq_tax_category_mapping_profile_category",
        ),
    )
    op.create_index(
        "ix_tax_category_mappings_profile_category",
        "tax_category_mappings",
        ["tax_profile_id", "category_id"],
    )

    op.create_table(
        "tax_transaction_overrides",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("tax_profile_id", sa.Uuid(), nullable=False),
        sa.Column("transaction_id", sa.Uuid(), nullable=False),
        sa.Column("tax_treatment", sa.String(length=40), nullable=False),
        sa.Column("deductibility_percentage", sa.Numeric(precision=9, scale=4), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["tax_profile_id"], ["tax_profiles.id"]),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tax_profile_id",
            "transaction_id",
            name="uq_tax_tx_override_profile_transaction",
        ),
    )
    op.create_index(
        "ix_tax_transaction_overrides_profile_transaction",
        "tax_transaction_overrides",
        ["tax_profile_id", "transaction_id"],
    )

    op.create_table(
        "tax_periods",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("tax_profile_id", sa.Uuid(), nullable=False),
        sa.Column("period_type", sa.String(length=20), nullable=False),
        sa.Column("date_from", sa.Date(), nullable=False),
        sa.Column("date_to", sa.Date(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["tax_profile_id"], ["tax_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tax_profile_id",
            "date_from",
            "date_to",
            name="uq_tax_periods_profile_range",
        ),
    )
    op.create_index(
        "ix_tax_periods_profile_range",
        "tax_periods",
        ["tax_profile_id", "date_from", "date_to"],
    )
    op.create_index("ix_tax_periods_organization_id", "tax_periods", ["organization_id"])

    op.create_table(
        "tax_calculations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("tax_period_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("gross_income", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("taxable_income", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("deductible_expenses", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("taxable_base", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("estimated_tax", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("calculated_by_user_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["tax_period_id"], ["tax_periods.id"]),
        sa.ForeignKeyConstraint(["calculated_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tax_period_id",
            "version",
            name="uq_tax_calculations_period_version",
        ),
    )
    op.create_index(
        "ix_tax_calculations_period_version",
        "tax_calculations",
        ["tax_period_id", "version"],
    )

    op.create_table(
        "tax_calculation_lines",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tax_calculation_id", sa.Uuid(), nullable=False),
        sa.Column("tax_rule_id", sa.Uuid(), nullable=False),
        sa.Column("description", sa.String(length=200), nullable=False),
        sa.Column("taxable_base", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("rate", sa.Numeric(precision=9, scale=4), nullable=True),
        sa.Column("calculated_amount", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.ForeignKeyConstraint(
            ["tax_calculation_id"], ["tax_calculations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["tax_rule_id"], ["tax_rules.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "tax_payments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("tax_period_id", sa.Uuid(), nullable=False),
        sa.Column("tax_type", sa.String(length=40), nullable=False),
        sa.Column("transaction_id", sa.Uuid(), nullable=False),
        sa.Column("source_account_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reference", sa.String(length=120), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("idempotency_key", sa.String(length=64), nullable=True),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["source_account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["tax_period_id"], ["tax_periods.id"]),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transaction_id", name="uq_tax_payments_transaction_id"),
    )
    op.create_index(
        "uq_tax_payments_org_idempotency",
        "tax_payments",
        ["organization_id", "idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )
    op.create_index(
        "ix_tax_payments_period_paid_at",
        "tax_payments",
        ["tax_period_id", "paid_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_tax_payments_period_paid_at", table_name="tax_payments")
    op.drop_index("uq_tax_payments_org_idempotency", table_name="tax_payments")
    op.drop_table("tax_payments")
    op.drop_index("ix_tax_calculations_period_version", table_name="tax_calculations")
    op.drop_table("tax_calculation_lines")
    op.drop_table("tax_calculations")
    op.drop_index("ix_tax_periods_organization_id", table_name="tax_periods")
    op.drop_index("ix_tax_periods_profile_range", table_name="tax_periods")
    op.drop_table("tax_periods")
    op.drop_index(
        "ix_tax_transaction_overrides_profile_transaction",
        table_name="tax_transaction_overrides",
    )
    op.drop_table("tax_transaction_overrides")
    op.drop_index("ix_tax_category_mappings_profile_category", table_name="tax_category_mappings")
    op.drop_table("tax_category_mappings")
    op.drop_table("tax_rule_categories")
    op.drop_index("ix_tax_rules_profile_active_effective", table_name="tax_rules")
    op.drop_table("tax_rules")
    op.drop_index("uq_tax_profiles_active_organization", table_name="tax_profiles")
    op.drop_index("ix_tax_profiles_organization_id_is_active", table_name="tax_profiles")
    op.drop_table("tax_profiles")
