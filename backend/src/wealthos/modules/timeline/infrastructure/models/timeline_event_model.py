"""SQLAlchemy model for timeline_events."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from wealthos.core.database import Base


class TimelineEventModel(Base):
    __tablename__ = "timeline_events"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "source_type",
            "event_type",
            "resource_id",
            "occurred_at",
            name="uq_timeline_events_idempotency",
        ),
        Index("ix_timeline_events_org_occurred_at", "organization_id", "occurred_at"),
        Index(
            "ix_timeline_events_org_source_occurred_at",
            "organization_id",
            "source_type",
            "occurred_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("organizations.id"),
        nullable=False,
    )
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_type: Mapped[str] = mapped_column(String(40), nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    importance: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(40), nullable=False)
    resource_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(19, 4), nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
