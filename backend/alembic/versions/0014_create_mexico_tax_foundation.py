"""Create Mexico tax foundation tables and category system codes.

Revision ID: 0014_mexico_tax_foundation
Revises: 0013_create_tax_foundation
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0014_mexico_tax_foundation"
down_revision: str | None = "0013_create_tax_foundation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("categories", sa.Column("system_code", sa.String(length=80), nullable=True))
    op.create_index(
        "uq_categories_org_system_code",
        "categories",
        ["organization_id", "system_code"],
        unique=True,
        postgresql_where=sa.text("system_code IS NOT NULL"),
    )

    op.create_table(
        "mx_tax_configurations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("tax_profile_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("rfc", sa.String(length=13), nullable=False),
        sa.Column("person_type", sa.String(length=20), nullable=False),
        sa.Column("tax_regime_code", sa.String(length=40), nullable=False),
        sa.Column("vat_enabled", sa.Boolean(), nullable=False),
        sa.Column("income_tax_enabled", sa.Boolean(), nullable=False),
        sa.Column("default_vat_rate", sa.Numeric(precision=9, scale=4), nullable=True),
        sa.Column("income_tax_estimation_method", sa.String(length=40), nullable=True),
        sa.Column("income_tax_estimation_base", sa.String(length=40), nullable=True),
        sa.Column("income_tax_estimation_rate", sa.Numeric(precision=9, scale=4), nullable=True),
        sa.Column("cash_flow_basis", sa.Boolean(), nullable=False),
        sa.Column("requires_invoice_evidence", sa.Boolean(), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["tax_profile_id"], ["tax_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tax_profile_id",
            "version",
            name="uq_mx_tax_configurations_profile_version",
        ),
    )
    op.create_index(
        "ix_mx_tax_configurations_org_profile",
        "mx_tax_configurations",
        ["organization_id", "tax_profile_id"],
    )
    op.create_index(
        "ix_mx_tax_configurations_profile_effective",
        "mx_tax_configurations",
        ["tax_profile_id", "effective_from", "effective_to"],
    )

    op.create_table(
        "mx_tax_category_mappings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("tax_profile_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("income_treatment", sa.String(length=40), nullable=True),
        sa.Column("expense_treatment", sa.String(length=40), nullable=True),
        sa.Column("vat_treatment", sa.String(length=40), nullable=False),
        sa.Column("deductibility_percentage", sa.Numeric(precision=9, scale=4), nullable=False),
        sa.Column("vat_creditable_percentage", sa.Numeric(precision=9, scale=4), nullable=False),
        sa.Column("requires_cfdi", sa.Boolean(), nullable=False),
        sa.Column("requires_payment_evidence", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["tax_profile_id"], ["tax_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tax_profile_id",
            "category_id",
            name="uq_mx_tax_category_mapping_profile_category",
        ),
    )
    op.create_index(
        "ix_mx_tax_category_mappings_org",
        "mx_tax_category_mappings",
        ["organization_id"],
    )

    op.create_table(
        "mx_tax_transaction_overrides",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("tax_profile_id", sa.Uuid(), nullable=False),
        sa.Column("transaction_id", sa.Uuid(), nullable=False),
        sa.Column("income_treatment", sa.String(length=40), nullable=True),
        sa.Column("expense_treatment", sa.String(length=40), nullable=True),
        sa.Column("vat_treatment", sa.String(length=40), nullable=False),
        sa.Column("deductibility_percentage", sa.Numeric(precision=9, scale=4), nullable=False),
        sa.Column("vat_creditable_percentage", sa.Numeric(precision=9, scale=4), nullable=False),
        sa.Column("requires_cfdi", sa.Boolean(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["tax_profile_id"], ["tax_profiles.id"]),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tax_profile_id",
            "transaction_id",
            name="uq_mx_tax_tx_override_profile_transaction",
        ),
    )
    op.create_index(
        "ix_mx_tax_tx_overrides_org",
        "mx_tax_transaction_overrides",
        ["organization_id"],
    )

    op.create_table(
        "mx_transaction_tax_details",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("transaction_id", sa.Uuid(), nullable=False),
        sa.Column("subtotal", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("vat_amount", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("withheld_income_tax", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("withheld_vat", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("other_taxes", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("total", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("calculation_source", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transaction_id", name="uq_mx_transaction_tax_details_tx"),
    )
    op.create_index(
        "ix_mx_transaction_tax_details_org",
        "mx_transaction_tax_details",
        ["organization_id"],
    )

    op.create_table(
        "mx_tax_withholdings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("transaction_id", sa.Uuid(), nullable=False),
        sa.Column("withholding_type", sa.String(length=40), nullable=False),
        sa.Column("base_amount", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("rate", sa.Numeric(precision=9, scale=4), nullable=True),
        sa.Column("amount", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("withheld_by_rfc", sa.String(length=13), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_mx_tax_withholdings_org_tx",
        "mx_tax_withholdings",
        ["organization_id", "transaction_id"],
    )

    op.create_table(
        "tax_evidence",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("transaction_id", sa.Uuid(), nullable=False),
        sa.Column("evidence_type", sa.String(length=40), nullable=False),
        sa.Column("external_reference", sa.String(length=200), nullable=True),
        sa.Column("issuer_rfc", sa.String(length=13), nullable=True),
        sa.Column("receiver_rfc", sa.String(length=13), nullable=True),
        sa.Column("document_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("subtotal", sa.Numeric(precision=19, scale=4), nullable=True),
        sa.Column("tax_amount", sa.Numeric(precision=19, scale=4), nullable=True),
        sa.Column("total", sa.Numeric(precision=19, scale=4), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("validation_status", sa.String(length=20), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_tax_evidence_org_tx",
        "tax_evidence",
        ["organization_id", "transaction_id"],
    )

    op.create_table(
        "mx_tax_calculation_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("tax_calculation_id", sa.Uuid(), nullable=False),
        sa.Column("configuration_version", sa.Integer(), nullable=False),
        sa.Column("catalog_version", sa.String(length=40), nullable=False),
        sa.Column("calculation_engine", sa.String(length=80), nullable=False),
        sa.Column("calculation_engine_version", sa.String(length=40), nullable=False),
        sa.Column("transaction_cutoff_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("workpaper_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["tax_calculation_id"], ["tax_calculations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tax_calculation_id",
            name="uq_mx_tax_calculation_snapshots_calculation",
        ),
    )
    op.create_index(
        "ix_mx_tax_calculation_snapshots_org",
        "mx_tax_calculation_snapshots",
        ["organization_id"],
    )

    op.create_table(
        "mx_tax_catalog_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("catalog_name", sa.String(length=60), nullable=False),
        sa.Column("catalog_version", sa.String(length=40), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("person_type", sa.String(length=20), nullable=True),
        sa.Column("rate", sa.Numeric(precision=9, scale=4), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("source_reference", sa.String(length=200), nullable=True),
        sa.Column("loaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("checksum", sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "catalog_name",
            "code",
            "catalog_version",
            name="uq_mx_tax_catalog_entries_name_code_version",
        ),
    )
    op.create_index(
        "ix_mx_tax_catalog_entries_name_active",
        "mx_tax_catalog_entries",
        ["catalog_name", "is_active"],
    )

    op.create_table(
        "mx_tax_payment_details",
        sa.Column("tax_payment_id", sa.Uuid(), nullable=False),
        sa.Column("payment_concept", sa.String(length=80), nullable=False),
        sa.Column("fiscal_period_reference", sa.String(length=80), nullable=True),
        sa.Column("authority_reference", sa.String(length=120), nullable=True),
        sa.Column("payment_line", sa.String(length=80), nullable=True),
        sa.Column("acknowledgment_reference", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tax_payment_id"], ["tax_payments.id"]),
        sa.PrimaryKeyConstraint("tax_payment_id"),
    )


def downgrade() -> None:
    op.drop_table("mx_tax_payment_details")
    op.drop_index("ix_mx_tax_catalog_entries_name_active", table_name="mx_tax_catalog_entries")
    op.drop_table("mx_tax_catalog_entries")
    op.drop_index("ix_mx_tax_calculation_snapshots_org", table_name="mx_tax_calculation_snapshots")
    op.drop_table("mx_tax_calculation_snapshots")
    op.drop_index("ix_tax_evidence_org_tx", table_name="tax_evidence")
    op.drop_table("tax_evidence")
    op.drop_index("ix_mx_tax_withholdings_org_tx", table_name="mx_tax_withholdings")
    op.drop_table("mx_tax_withholdings")
    op.drop_index("ix_mx_transaction_tax_details_org", table_name="mx_transaction_tax_details")
    op.drop_table("mx_transaction_tax_details")
    op.drop_index("ix_mx_tax_tx_overrides_org", table_name="mx_tax_transaction_overrides")
    op.drop_table("mx_tax_transaction_overrides")
    op.drop_index("ix_mx_tax_category_mappings_org", table_name="mx_tax_category_mappings")
    op.drop_table("mx_tax_category_mappings")
    op.drop_index("ix_mx_tax_configurations_profile_effective", table_name="mx_tax_configurations")
    op.drop_index("ix_mx_tax_configurations_org_profile", table_name="mx_tax_configurations")
    op.drop_table("mx_tax_configurations")
    op.drop_index("uq_categories_org_system_code", table_name="categories")
    op.drop_column("categories", "system_code")
