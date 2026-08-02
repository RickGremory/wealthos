"""SQLAlchemy model for fx_transfers."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from wealthos.core.database import Base


class FxTransferModel(Base):
    __tablename__ = "fx_transfers"
    __table_args__ = (
        Index("ix_fx_transfers_organization_id", "organization_id"),
        Index(
            "ix_fx_transfers_organization_id_occurred_at",
            "organization_id",
            "occurred_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id"), nullable=False
    )
    source_account_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("accounts.id"), nullable=False
    )
    destination_account_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("accounts.id"), nullable=False
    )
    source_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    source_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    destination_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    destination_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    effective_exchange_rate: Mapped[Decimal] = mapped_column(
        Numeric(24, 10), nullable=False
    )
    fee_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    fee_currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_transaction_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("transactions.id"), nullable=False
    )
    destination_transaction_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("transactions.id"), nullable=False
    )
    fee_transaction_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("transactions.id"), nullable=True
    )
    created_by_user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
