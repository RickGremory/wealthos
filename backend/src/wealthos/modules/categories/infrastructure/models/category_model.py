"""SQLAlchemy model for categories."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from wealthos.core.database import Base


class CategoryModel(Base):
    """Persistence mapping for the Category aggregate."""

    __tablename__ = "categories"
    __table_args__ = (
        Index("ix_categories_organization_id", "organization_id"),
        Index(
            "ix_categories_organization_id_category_type",
            "organization_id",
            "category_type",
        ),
        Index("ix_categories_organization_id_is_active", "organization_id", "is_active"),
        Index("ix_categories_parent_id", "parent_id"),
        Index(
            "uq_categories_org_parent_norm_type",
            "organization_id",
            "parent_id",
            "normalized_name",
            "category_type",
            unique=True,
            postgresql_nulls_not_distinct=True,
        ),
        Index(
            "uq_categories_org_system_code",
            "organization_id",
            "system_code",
            unique=True,
            postgresql_where=text("system_code IS NOT NULL"),
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("organizations.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(80), nullable=False)
    category_type: Mapped[str] = mapped_column(String(20), nullable=False)
    parent_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=True,
    )
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    system_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
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
        default=None,
    )
