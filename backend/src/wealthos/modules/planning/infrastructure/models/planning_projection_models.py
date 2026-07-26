"""SQLAlchemy models for the planning projection spine (SPEC-004 §4).

Only settings and manual planned cash flows persist. Safe To Spend,
projections, breakdowns and scenarios are always calculated.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
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
from sqlalchemy.orm import Mapped, mapped_column

from wealthos.core.database import Base


class PlanningSettingsModel(Base):
    __tablename__ = "planning_settings"
    __table_args__ = (
        UniqueConstraint("organization_id", name="uq_planning_settings_organization_id"),
        CheckConstraint(
            "safety_reserve_amount IS NULL OR safety_reserve_amount >= 0",
            name="ck_planning_settings_reserve_amount_non_negative",
        ),
        CheckConstraint(
            "default_horizon IN ('today', '7_days', '30_days', '90_days')",
            name="ck_planning_settings_default_horizon",
        ),
        CheckConstraint(
            "safety_reserve_strategy IN "
            "('none', 'fixed_amount', 'linked_goal', 'percentage_of_cash', 'days_of_expenses')",
            name="ck_planning_settings_reserve_strategy",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("organizations.id"),
        nullable=False,
    )
    default_horizon: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="30_days",
    )
    safety_reserve_strategy: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="none",
    )
    safety_reserve_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(19, 4),
        nullable=True,
    )
    # Soft reference: validated through the Goals port, not a FK, so deleting a
    # goal never blocks Planning.
    linked_emergency_goal_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    include_expected_income: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    include_estimated_expenses: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
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


class PlannedCashFlowModel(Base):
    __tablename__ = "planned_cash_flows"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_planned_cash_flows_amount_positive"),
        CheckConstraint(
            "direction IN ('inflow', 'outflow')",
            name="ck_planned_cash_flows_direction",
        ),
        CheckConstraint(
            "certainty IN ('confirmed', 'expected', 'estimated')",
            name="ck_planned_cash_flows_certainty",
        ),
        CheckConstraint(
            "status IN ('active', 'settled', 'cancelled', 'expired')",
            name="ck_planned_cash_flows_status",
        ),
        Index(
            "ix_planned_cash_flows_org_currency_expected_at",
            "organization_id",
            "currency",
            "expected_at",
        ),
        Index("ix_planned_cash_flows_org_status", "organization_id", "status"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("organizations.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    expected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    certainty: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    settled_transaction_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("transactions.id"),
        nullable=True,
    )
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
