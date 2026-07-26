"""SQLAlchemy models for debts and debt payments."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
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
from sqlalchemy.orm import Mapped, mapped_column

from wealthos.core.database import Base


class DebtModel(Base):
    __tablename__ = "debts"
    __table_args__ = (
        UniqueConstraint("account_id", name="debts_account_unique_idx"),
        Index("debts_organization_status_idx", "organization_id", "status"),
        Index("debts_organization_currency_idx", "organization_id", "currency"),
        Index("debts_organization_due_day_idx", "organization_id", "due_day"),
        Index("debts_organization_priority_idx", "organization_id", "priority"),
        Index("ix_debts_organization_id_debt_type", "organization_id", "debt_type"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("organizations.id"),
        nullable=False,
    )
    account_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("accounts.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    debt_type: Mapped[str] = mapped_column(String(30), nullable=False)
    creditor: Mapped[str | None] = mapped_column(String(120), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    priority: Mapped[str] = mapped_column(String(10), nullable=False, default="medium")
    interest_rate: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    minimum_payment: Mapped[Decimal | None] = mapped_column(Numeric(19, 4), nullable=True)
    scheduled_payment: Mapped[Decimal | None] = mapped_column(
        Numeric(19, 4),
        nullable=True,
    )
    credit_limit: Mapped[Decimal | None] = mapped_column(Numeric(19, 4), nullable=True)
    original_amount: Mapped[Decimal | None] = mapped_column(Numeric(19, 4), nullable=True)
    statement_day: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    due_day: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    maturity_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class DebtPaymentModel(Base):
    __tablename__ = "debt_payments"
    __table_args__ = (
        Index(
            "ix_debt_payments_organization_id_debt_id_paid_at",
            "organization_id",
            "debt_id",
            "paid_at",
        ),
        Index(
            "uq_debt_payments_transaction_id",
            "transaction_id",
            unique=True,
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("organizations.id"),
        nullable=False,
    )
    debt_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("debts.id"),
        nullable=False,
    )
    transaction_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("transactions.id"),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    principal_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(19, 4),
        nullable=True,
    )
    interest_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(19, 4),
        nullable=True,
    )
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by_user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
