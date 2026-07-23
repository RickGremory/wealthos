"""Align organizations table with domain model (lengths + soft delete).

Revision ID: 0003_align_organizations
Revises: 0002_create_organizations
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_align_organizations"
down_revision: str | None = "0002_create_organizations"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.alter_column(
        "organizations",
        "name",
        existing_type=sa.VARCHAR(length=100),
        type_=sa.String(length=120),
        existing_nullable=False,
    )
    op.alter_column(
        "organizations",
        "slug",
        existing_type=sa.VARCHAR(length=100),
        type_=sa.String(length=80),
        existing_nullable=False,
    )
    op.alter_column(
        "organizations",
        "locale",
        existing_type=sa.VARCHAR(length=5),
        type_=sa.String(length=16),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "organizations",
        "locale",
        existing_type=sa.String(length=16),
        type_=sa.VARCHAR(length=5),
        existing_nullable=False,
    )
    op.alter_column(
        "organizations",
        "slug",
        existing_type=sa.String(length=80),
        type_=sa.VARCHAR(length=100),
        existing_nullable=False,
    )
    op.alter_column(
        "organizations",
        "name",
        existing_type=sa.String(length=120),
        type_=sa.VARCHAR(length=100),
        existing_nullable=False,
    )
    op.drop_column("organizations", "deleted_at")
