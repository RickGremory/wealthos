"""SQLAlchemy models for budgets and cash planning."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    PrimaryKeyConstraint,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from wealthos.core.database import Base


class BudgetModel(Base):
    __tablename__ = "budgets"
    __table_args__ = (
        CheckConstraint("date_from <= date_to", name="ck_budgets_date_range"),
        Index(
            "ix_budgets_organization_id_status_date_from_date_to",
            "organization_id",
            "status",
            "date_from",
            "date_to",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("organizations.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    period_type: Mapped[str] = mapped_column(String(20), nullable=False)
    date_from: Mapped[date] = mapped_column(Date, nullable=False)
    date_to: Mapped[date] = mapped_column(Date, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    rollover_policy: Mapped[str] = mapped_column(String(20), nullable=False)
    forecast_method: Mapped[str] = mapped_column(String(20), nullable=False)
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


class BudgetAllocationModel(Base):
    """Planned amount within a budget.

    UniqueConstraint on (budget_id, allocation_type, category_id, goal_id,
    debt_id, tax_profile_id): PostgreSQL treats NULLs as distinct in unique
    indexes, so application-level validation may still be needed for rows
    that differ only by NULL reference columns.
    """

    __tablename__ = "budget_allocations"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_budget_allocations_amount_positive"),
        UniqueConstraint(
            "budget_id",
            "allocation_type",
            "category_id",
            "goal_id",
            "debt_id",
            "tax_profile_id",
            name="uq_budget_allocations_type_refs",
        ),
        Index(
            "ix_budget_allocations_budget_id_allocation_type",
            "budget_id",
            "allocation_type",
        ),
        Index("ix_budget_allocations_category_id", "category_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("organizations.id"),
        nullable=False,
    )
    budget_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("budgets.id"),
        nullable=False,
    )
    allocation_type: Mapped[str] = mapped_column(String(30), nullable=False)
    category_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("categories.id"),
        nullable=True,
    )
    goal_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("goals.id"),
        nullable=True,
    )
    debt_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("debts.id"),
        nullable=True,
    )
    tax_profile_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("tax_profiles.id"),
        nullable=True,
    )
    destination_account_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("accounts.id"),
        nullable=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
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


class BudgetAllocationMatchModel(Base):
    __tablename__ = "budget_allocation_matches"
    __table_args__ = (
        CheckConstraint(
            "matched_amount > 0",
            name="ck_budget_allocation_matches_amount_positive",
        ),
        UniqueConstraint(
            "budget_allocation_id",
            "transaction_id",
            name="uq_budget_allocation_matches_allocation_tx",
        ),
        Index(
            "ix_budget_allocation_matches_budget_allocation_id",
            "budget_allocation_id",
        ),
        Index("ix_budget_allocation_matches_transaction_id", "transaction_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("organizations.id"),
        nullable=False,
    )
    budget_allocation_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("budget_allocations.id"),
        nullable=False,
    )
    transaction_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("transactions.id"),
        nullable=False,
    )
    matched_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )


class CashPlanModel(Base):
    __tablename__ = "cash_plans"
    __table_args__ = (
        CheckConstraint("date_from <= date_to", name="ck_cash_plans_date_range"),
        Index(
            "ix_cash_plans_organization_id_status_date_from_date_to",
            "organization_id",
            "status",
            "date_from",
            "date_to",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("organizations.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    date_from: Mapped[date] = mapped_column(Date, nullable=False)
    date_to: Mapped[date] = mapped_column(Date, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    opening_balance_mode: Mapped[str] = mapped_column(String(30), nullable=False)
    manual_opening_balance: Mapped[Decimal | None] = mapped_column(
        Numeric(19, 4),
        nullable=True,
    )
    minimum_cash_buffer_type: Mapped[str] = mapped_column(String(40), nullable=False)
    minimum_cash_buffer_value: Mapped[Decimal] = mapped_column(
        Numeric(19, 4),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
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


class CashPlanAccountModel(Base):
    __tablename__ = "cash_plan_accounts"
    __table_args__ = (
        PrimaryKeyConstraint("cash_plan_id", "account_id"),
        Index("ix_cash_plan_accounts_account_id", "account_id"),
    )

    cash_plan_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("cash_plans.id"),
        nullable=False,
    )
    account_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("accounts.id"),
        nullable=False,
    )


class CashPlanItemModel(Base):
    __tablename__ = "cash_plan_items"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_cash_plan_items_amount_positive"),
        CheckConstraint(
            "probability >= 0 AND probability <= 100",
            name="ck_cash_plan_items_probability_range",
        ),
        Index(
            "ix_cash_plan_items_cash_plan_id_expected_date_status",
            "cash_plan_id",
            "expected_date",
            "status",
        ),
        Index(
            "ix_cash_plan_items_linked_entity_type_linked_entity_id",
            "linked_entity_type",
            "linked_entity_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("organizations.id"),
        nullable=False,
    )
    cash_plan_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("cash_plans.id"),
        nullable=False,
    )
    item_type: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    expected_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    probability: Mapped[Decimal] = mapped_column(Numeric(9, 4), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    category_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("categories.id"),
        nullable=True,
    )
    account_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("accounts.id"),
        nullable=True,
    )
    linked_entity_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    linked_entity_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    recurrence_rule: Mapped[str | None] = mapped_column(String(255), nullable=True)
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
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class CashPlanItemMatchModel(Base):
    __tablename__ = "cash_plan_item_matches"
    __table_args__ = (
        CheckConstraint(
            "matched_amount > 0",
            name="ck_cash_plan_item_matches_amount_positive",
        ),
        UniqueConstraint(
            "cash_plan_item_id",
            "transaction_id",
            name="uq_cash_plan_item_matches_item_tx",
        ),
        Index("ix_cash_plan_item_matches_cash_plan_item_id", "cash_plan_item_id"),
        Index("ix_cash_plan_item_matches_transaction_id", "transaction_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("organizations.id"),
        nullable=False,
    )
    cash_plan_item_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("cash_plan_items.id"),
        nullable=False,
    )
    transaction_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("transactions.id"),
        nullable=False,
    )
    matched_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
