"""SQLAlchemy models for goals."""

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
    PrimaryKeyConstraint,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from wealthos.core.database import Base


class GoalModel(Base):
    __tablename__ = "goals"
    __table_args__ = (
        Index("ix_goals_organization_id", "organization_id"),
        Index("ix_goals_organization_id_status", "organization_id", "status"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("organizations.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    strategy: Mapped[str] = mapped_column(String(40), nullable=False)
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
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    account_links: Mapped[list[GoalAccountModel]] = relationship(
        "GoalAccountModel",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    manual_progress: Mapped[GoalManualProgressModel | None] = relationship(
        "GoalManualProgressModel",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )


class GoalAccountModel(Base):
    __tablename__ = "goal_accounts"
    __table_args__ = (
        PrimaryKeyConstraint("goal_id", "account_id"),
        Index("ix_goal_accounts_account_id", "account_id"),
    )

    goal_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("goals.id", ondelete="CASCADE"),
        nullable=False,
    )
    account_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("accounts.id"),
        nullable=False,
    )


class GoalManualProgressModel(Base):
    __tablename__ = "goal_manual_progress"

    goal_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("goals.id", ondelete="CASCADE"),
        primary_key=True,
    )
    current_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
