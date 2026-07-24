"""Create categories table.

Revision ID: 0007_create_categories
Revises: 0006_create_accounts
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007_create_categories"
down_revision: str | None = "0006_create_accounts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("normalized_name", sa.String(length=80), nullable=False),
        sa.Column("category_type", sa.String(length=20), nullable=False),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("icon", sa.String(length=50), nullable=True),
        sa.Column("color", sa.String(length=20), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["parent_id"], ["categories.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_categories_organization_id", "categories", ["organization_id"])
    op.create_index(
        "ix_categories_organization_id_category_type",
        "categories",
        ["organization_id", "category_type"],
    )
    op.create_index(
        "ix_categories_organization_id_is_active",
        "categories",
        ["organization_id", "is_active"],
    )
    op.create_index("ix_categories_parent_id", "categories", ["parent_id"])
    op.create_index(
        "uq_categories_org_parent_norm_type",
        "categories",
        ["organization_id", "parent_id", "normalized_name", "category_type"],
        unique=True,
        postgresql_nulls_not_distinct=True,
    )


def downgrade() -> None:
    op.drop_index("uq_categories_org_parent_norm_type", table_name="categories")
    op.drop_index("ix_categories_parent_id", table_name="categories")
    op.drop_index("ix_categories_organization_id_is_active", table_name="categories")
    op.drop_index("ix_categories_organization_id_category_type", table_name="categories")
    op.drop_index("ix_categories_organization_id", table_name="categories")
    op.drop_table("categories")
