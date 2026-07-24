"""SQLAlchemy models for the taxes foundation."""

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
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from wealthos.core.database import Base


class TaxProfileModel(Base):
    __tablename__ = "tax_profiles"
    __table_args__ = (
        Index("ix_tax_profiles_organization_id_is_active", "organization_id", "is_active"),
        Index(
            "uq_tax_profiles_active_organization",
            "organization_id",
            unique=True,
            postgresql_where=text("is_active IS TRUE"),
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id"), nullable=False
    )
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    jurisdiction: Mapped[str | None] = mapped_column(String(120), nullable=True)
    taxpayer_type: Mapped[str] = mapped_column(String(30), nullable=False)
    tax_regime: Mapped[str | None] = mapped_column(String(120), nullable=True)
    filing_frequency: Mapped[str] = mapped_column(String(20), nullable=False)
    fiscal_year_start_month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    reserve_account_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("accounts.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )


class TaxRuleModel(Base):
    __tablename__ = "tax_rules"
    __table_args__ = (
        Index(
            "ix_tax_rules_profile_active_effective",
            "tax_profile_id",
            "is_active",
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
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    tax_type: Mapped[str] = mapped_column(String(40), nullable=False)
    calculation_method: Mapped[str] = mapped_column(String(20), nullable=False)
    rate: Mapped[Decimal | None] = mapped_column(Numeric(9, 4), nullable=True)
    fixed_amount: Mapped[Decimal | None] = mapped_column(Numeric(19, 4), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    applies_to: Mapped[str] = mapped_column(String(40), nullable=False)
    tax_inclusion_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TaxRuleCategoryModel(Base):
    __tablename__ = "tax_rule_categories"
    __table_args__ = (UniqueConstraint("tax_rule_id", "category_id", name="uq_tax_rule_category"),)

    tax_rule_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("tax_rules.id", ondelete="CASCADE"), primary_key=True
    )
    category_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("categories.id"), primary_key=True)


class TaxCategoryMappingModel(Base):
    __tablename__ = "tax_category_mappings"
    __table_args__ = (
        UniqueConstraint(
            "tax_profile_id",
            "category_id",
            name="uq_tax_category_mapping_profile_category",
        ),
        Index("ix_tax_category_mappings_profile_category", "tax_profile_id", "category_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id"), nullable=False
    )
    tax_profile_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("tax_profiles.id"), nullable=False
    )
    category_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("categories.id"), nullable=False)
    tax_treatment: Mapped[str] = mapped_column(String(40), nullable=False)
    deductibility_percentage: Mapped[Decimal] = mapped_column(
        Numeric(9, 4), nullable=False, default=Decimal("100")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )


class TaxTransactionOverrideModel(Base):
    __tablename__ = "tax_transaction_overrides"
    __table_args__ = (
        UniqueConstraint(
            "tax_profile_id",
            "transaction_id",
            name="uq_tax_tx_override_profile_transaction",
        ),
        Index(
            "ix_tax_transaction_overrides_profile_transaction",
            "tax_profile_id",
            "transaction_id",
        ),
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
    tax_treatment: Mapped[str] = mapped_column(String(40), nullable=False)
    deductibility_percentage: Mapped[Decimal] = mapped_column(
        Numeric(9, 4), nullable=False, default=Decimal("100")
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )


class TaxPeriodModel(Base):
    __tablename__ = "tax_periods"
    __table_args__ = (
        UniqueConstraint(
            "tax_profile_id",
            "date_from",
            "date_to",
            name="uq_tax_periods_profile_range",
        ),
        Index("ix_tax_periods_profile_range", "tax_profile_id", "date_from", "date_to"),
        Index("ix_tax_periods_organization_id", "organization_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id"), nullable=False
    )
    tax_profile_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("tax_profiles.id"), nullable=False
    )
    period_type: Mapped[str] = mapped_column(String(20), nullable=False)
    date_from: Mapped[date] = mapped_column(Date, nullable=False)
    date_to: Mapped[date] = mapped_column(Date, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    calculated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )


class TaxCalculationModel(Base):
    __tablename__ = "tax_calculations"
    __table_args__ = (
        UniqueConstraint(
            "tax_period_id",
            "version",
            name="uq_tax_calculations_period_version",
        ),
        Index("ix_tax_calculations_period_version", "tax_period_id", "version"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id"), nullable=False
    )
    tax_period_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("tax_periods.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    gross_income: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    taxable_income: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    deductible_expenses: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    taxable_base: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    estimated_tax: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    calculated_by_user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )


class TaxCalculationLineModel(Base):
    __tablename__ = "tax_calculation_lines"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    tax_calculation_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("tax_calculations.id", ondelete="CASCADE"), nullable=False
    )
    tax_rule_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("tax_rules.id"), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    taxable_base: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    rate: Mapped[Decimal | None] = mapped_column(Numeric(9, 4), nullable=True)
    calculated_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)


class TaxPaymentModel(Base):
    __tablename__ = "tax_payments"
    __table_args__ = (
        UniqueConstraint("transaction_id", name="uq_tax_payments_transaction_id"),
        Index(
            "uq_tax_payments_org_idempotency",
            "organization_id",
            "idempotency_key",
            unique=True,
            postgresql_where=text("idempotency_key IS NOT NULL"),
        ),
        Index("ix_tax_payments_period_paid_at", "tax_period_id", "paid_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id"), nullable=False
    )
    tax_period_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("tax_periods.id"), nullable=False)
    tax_type: Mapped[str] = mapped_column(String(40), nullable=False)
    transaction_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("transactions.id"), nullable=False
    )
    source_account_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("accounts.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_by_user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
