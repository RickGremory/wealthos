"""SQLAlchemy models for Mexico tax foundation."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from wealthos.core.database import Base


class MexicoTaxConfigurationModel(Base):
    __tablename__ = "mx_tax_configurations"
    __table_args__ = (
        UniqueConstraint(
            "tax_profile_id",
            "version",
            name="uq_mx_tax_configurations_profile_version",
        ),
        Index("ix_mx_tax_configurations_org_profile", "organization_id", "tax_profile_id"),
        Index(
            "ix_mx_tax_configurations_profile_effective",
            "tax_profile_id",
            "effective_from",
            "effective_to",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id"), nullable=False
    )
    tax_profile_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("tax_profiles.id"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    rfc: Mapped[str] = mapped_column(String(13), nullable=False)
    person_type: Mapped[str] = mapped_column(String(20), nullable=False)
    tax_regime_code: Mapped[str] = mapped_column(String(40), nullable=False)
    vat_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    income_tax_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    default_vat_rate: Mapped[Decimal | None] = mapped_column(Numeric(9, 4), nullable=True)
    income_tax_estimation_method: Mapped[str | None] = mapped_column(String(40), nullable=True)
    income_tax_estimation_base: Mapped[str | None] = mapped_column(String(40), nullable=True)
    income_tax_estimation_rate: Mapped[Decimal | None] = mapped_column(Numeric(9, 4), nullable=True)
    cash_flow_basis: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    requires_invoice_evidence: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )


class MexicoTaxCategoryMappingModel(Base):
    __tablename__ = "mx_tax_category_mappings"
    __table_args__ = (
        UniqueConstraint(
            "tax_profile_id",
            "category_id",
            name="uq_mx_tax_category_mapping_profile_category",
        ),
        Index("ix_mx_tax_category_mappings_org", "organization_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id"), nullable=False
    )
    tax_profile_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("tax_profiles.id"), nullable=False
    )
    category_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("categories.id"), nullable=False)
    income_treatment: Mapped[str | None] = mapped_column(String(40), nullable=True)
    expense_treatment: Mapped[str | None] = mapped_column(String(40), nullable=True)
    vat_treatment: Mapped[str] = mapped_column(String(40), nullable=False)
    deductibility_percentage: Mapped[Decimal] = mapped_column(
        Numeric(9, 4), nullable=False, default=Decimal("100")
    )
    vat_creditable_percentage: Mapped[Decimal] = mapped_column(
        Numeric(9, 4), nullable=False, default=Decimal("100")
    )
    requires_cfdi: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    requires_payment_evidence: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )


class MexicoTaxTransactionOverrideModel(Base):
    __tablename__ = "mx_tax_transaction_overrides"
    __table_args__ = (
        UniqueConstraint(
            "tax_profile_id",
            "transaction_id",
            name="uq_mx_tax_tx_override_profile_transaction",
        ),
        Index("ix_mx_tax_tx_overrides_org", "organization_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id"), nullable=False
    )
    tax_profile_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("tax_profiles.id"), nullable=False
    )
    transaction_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("transactions.id"), nullable=False
    )
    income_treatment: Mapped[str | None] = mapped_column(String(40), nullable=True)
    expense_treatment: Mapped[str | None] = mapped_column(String(40), nullable=True)
    vat_treatment: Mapped[str] = mapped_column(String(40), nullable=False)
    deductibility_percentage: Mapped[Decimal] = mapped_column(
        Numeric(9, 4), nullable=False, default=Decimal("100")
    )
    vat_creditable_percentage: Mapped[Decimal] = mapped_column(
        Numeric(9, 4), nullable=False, default=Decimal("100")
    )
    requires_cfdi: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )


class MexicoTransactionTaxDetailsModel(Base):
    __tablename__ = "mx_transaction_tax_details"
    __table_args__ = (
        UniqueConstraint("transaction_id", name="uq_mx_transaction_tax_details_tx"),
        Index("ix_mx_transaction_tax_details_org", "organization_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id"), nullable=False
    )
    transaction_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("transactions.id"), nullable=False
    )
    subtotal: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    vat_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    withheld_income_tax: Mapped[Decimal] = mapped_column(
        Numeric(19, 4), nullable=False, default=Decimal("0")
    )
    withheld_vat: Mapped[Decimal] = mapped_column(
        Numeric(19, 4), nullable=False, default=Decimal("0")
    )
    other_taxes: Mapped[Decimal] = mapped_column(
        Numeric(19, 4), nullable=False, default=Decimal("0")
    )
    total: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    calculation_source: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )


class MexicoTaxWithholdingModel(Base):
    __tablename__ = "mx_tax_withholdings"
    __table_args__ = (Index("ix_mx_tax_withholdings_org_tx", "organization_id", "transaction_id"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id"), nullable=False
    )
    transaction_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("transactions.id"), nullable=False
    )
    withholding_type: Mapped[str] = mapped_column(String(40), nullable=False)
    base_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    rate: Mapped[Decimal | None] = mapped_column(Numeric(9, 4), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    withheld_by_rfc: Mapped[str | None] = mapped_column(String(13), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )


class TaxEvidenceModel(Base):
    __tablename__ = "tax_evidence"
    __table_args__ = (Index("ix_tax_evidence_org_tx", "organization_id", "transaction_id"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id"), nullable=False
    )
    transaction_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("transactions.id"), nullable=False
    )
    evidence_type: Mapped[str] = mapped_column(String(40), nullable=False)
    external_reference: Mapped[str | None] = mapped_column(String(200), nullable=True)
    issuer_rfc: Mapped[str | None] = mapped_column(String(13), nullable=True)
    receiver_rfc: Mapped[str | None] = mapped_column(String(13), nullable=True)
    document_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    subtotal: Mapped[Decimal | None] = mapped_column(Numeric(19, 4), nullable=True)
    tax_amount: Mapped[Decimal | None] = mapped_column(Numeric(19, 4), nullable=True)
    total: Mapped[Decimal | None] = mapped_column(Numeric(19, 4), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    validation_status: Mapped[str] = mapped_column(String(20), nullable=False)
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )


class MexicoTaxCalculationSnapshotModel(Base):
    __tablename__ = "mx_tax_calculation_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "tax_calculation_id",
            name="uq_mx_tax_calculation_snapshots_calculation",
        ),
        Index("ix_mx_tax_calculation_snapshots_org", "organization_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id"), nullable=False
    )
    tax_calculation_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("tax_calculations.id"), nullable=False
    )
    configuration_version: Mapped[int] = mapped_column(Integer, nullable=False)
    catalog_version: Mapped[str] = mapped_column(String(40), nullable=False)
    calculation_engine: Mapped[str] = mapped_column(String(80), nullable=False)
    calculation_engine_version: Mapped[str] = mapped_column(String(40), nullable=False)
    transaction_cutoff_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    workpaper_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )


class MxTaxCatalogEntryModel(Base):
    __tablename__ = "mx_tax_catalog_entries"
    __table_args__ = (
        UniqueConstraint(
            "catalog_name",
            "code",
            "catalog_version",
            name="uq_mx_tax_catalog_entries_name_code_version",
        ),
        Index("ix_mx_tax_catalog_entries_name_active", "catalog_name", "is_active"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    catalog_name: Mapped[str] = mapped_column(String(60), nullable=False)
    catalog_version: Mapped[str] = mapped_column(String(40), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    person_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rate: Mapped[Decimal | None] = mapped_column(Numeric(9, 4), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    source_reference: Mapped[str | None] = mapped_column(String(200), nullable=True)
    loaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)


class MxTaxPaymentDetailModel(Base):
    __tablename__ = "mx_tax_payment_details"
    __table_args__ = (UniqueConstraint("tax_payment_id", name="uq_mx_tax_payment_details_payment"),)

    tax_payment_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("tax_payments.id"), primary_key=True
    )
    payment_concept: Mapped[str] = mapped_column(String(80), nullable=False)
    fiscal_period_reference: Mapped[str | None] = mapped_column(String(80), nullable=True)
    authority_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    payment_line: Mapped[str | None] = mapped_column(String(80), nullable=True)
    acknowledgment_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
