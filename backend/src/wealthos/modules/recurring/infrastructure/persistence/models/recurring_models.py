"""SQLAlchemy models for Recurring Engine (SPEC-005)."""

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
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from wealthos.core.database import Base


class RecurringRuleModel(Base):
    __tablename__ = "recurring_rules"
    __table_args__ = (
        Index("ix_recurring_rules_org_status", "organization_id", "status"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("organizations.id"),
        nullable=False,
    )
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    related_resource_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    related_resource_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    versions: Mapped[list[RecurringRuleVersionModel]] = relationship(
        back_populates="rule",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    pauses: Mapped[list[RecurringRulePauseModel]] = relationship(
        back_populates="rule",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    exceptions: Mapped[list[RecurringOccurrenceExceptionModel]] = relationship(
        back_populates="rule",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class RecurringRuleVersionModel(Base):
    __tablename__ = "recurring_rule_versions"
    __table_args__ = (
        Index(
            "ix_recurring_versions_rule_effective",
            "recurring_rule_id",
            "effective_from",
            "effective_until",
        ),
        Index(
            "ix_recurring_versions_org_currency",
            "organization_id",
            "currency",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    recurring_rule_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("recurring_rules.id", ondelete="CASCADE"),
        nullable=False,
    )
    organization_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("organizations.id"),
        nullable=False,
    )
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    amount_strategy: Mapped[str] = mapped_column(String(20), nullable=False)
    certainty: Mapped[str] = mapped_column(String(20), nullable=False)
    settlement_mode: Mapped[str] = mapped_column(String(30), nullable=False)
    frequency: Mapped[str] = mapped_column(String(10), nullable=False)
    interval: Mapped[int] = mapped_column(Integer, nullable=False)
    days_of_week: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    day_of_month: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    month_of_year: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    end_of_month: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    invalid_date_policy: Mapped[str] = mapped_column(String(30), nullable=False)
    starts_on: Mapped[date] = mapped_column(Date, nullable=False)
    ends_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    grace_period_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    account_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    destination_account_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    category_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    rule: Mapped[RecurringRuleModel] = relationship(back_populates="versions")


class RecurringRulePauseModel(Base):
    __tablename__ = "recurring_rule_pauses"
    __table_args__ = (
        Index(
            "ix_recurring_pauses_rule_dates",
            "recurring_rule_id",
            "starts_on",
            "ends_on",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    recurring_rule_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("recurring_rules.id", ondelete="CASCADE"),
        nullable=False,
    )
    organization_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("organizations.id"),
        nullable=False,
    )
    starts_on: Mapped[date] = mapped_column(Date, nullable=False)
    ends_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    rule: Mapped[RecurringRuleModel] = relationship(back_populates="pauses")


class RecurringOccurrenceExceptionModel(Base):
    __tablename__ = "recurring_occurrence_exceptions"
    __table_args__ = (
        Index(
            "ix_recurring_exceptions_rule_original_date",
            "recurring_rule_id",
            "original_expected_on",
        ),
        Index(
            "ix_recurring_exceptions_replacement_date",
            "recurring_rule_id",
            "replacement_expected_on",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("organizations.id"),
        nullable=False,
    )
    recurring_rule_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("recurring_rules.id", ondelete="CASCADE"),
        nullable=False,
    )
    original_occurrence_key: Mapped[str] = mapped_column(String(120), nullable=False)
    original_expected_on: Mapped[date] = mapped_column(Date, nullable=False)
    exception_type: Mapped[str] = mapped_column(String(30), nullable=False)
    replacement_expected_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    replacement_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(19, 4),
        nullable=True,
    )
    replacement_certainty: Mapped[str | None] = mapped_column(String(20), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    deactivated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    rule: Mapped[RecurringRuleModel] = relationship(back_populates="exceptions")


class RecurringOccurrenceSettlementModel(Base):
    __tablename__ = "recurring_occurrence_settlements"
    __table_args__ = (
        UniqueConstraint(
            "occurrence_key",
            "transaction_id",
            name="uq_recurring_settlements_occurrence_transaction",
        ),
        Index(
            "ix_recurring_settlements_occurrence",
            "organization_id",
            "occurrence_key",
        ),
        Index("ix_recurring_settlements_transaction", "transaction_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("organizations.id"),
        nullable=False,
    )
    recurring_rule_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("recurring_rules.id", ondelete="CASCADE"),
        nullable=False,
    )
    occurrence_key: Mapped[str] = mapped_column(String(120), nullable=False)
    transaction_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("transactions.id"),
        nullable=False,
    )
    settled_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    link_type: Mapped[str] = mapped_column(String(30), nullable=False)
    linked_by: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    linked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    voided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
