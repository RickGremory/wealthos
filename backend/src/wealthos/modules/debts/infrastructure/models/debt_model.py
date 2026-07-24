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
    Numeric,
    SmallInteger,
    String,
    Text,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from wealthos.core.database import Base


class DebtModel(Base):
    __tablename__ = "debts"
    __table_args__ = (
        Index("ix_debts_organization_id_status", "organization_id", "status"),
        Index("ix_debts_organization_id_debt_type", "organization_id", "debt_type"),
        Index("ix_debts_account_id", "account_id"),
        Index(
            "uq_active_debt_account",
            "account_id",
            unique=True,
            postgresql_where=text(
                "status IN ('active', 'paid_off') AND archived_at IS NULL"
            ),
        ),
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
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    annual_interest_rate: Mapped[Decimal] = mapped_column(
        Numeric(9, 4),
        nullable=False,
    )
    minimum_payment: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    original_principal: Mapped[Decimal | None] = mapped_column(
        Numeric(19, 4),
        nullable=True,
    )
    opened_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    maturity_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    payment_day: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    statement_day: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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
    paid_off_at: Mapped[datetime | None] = mapped_column(
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
