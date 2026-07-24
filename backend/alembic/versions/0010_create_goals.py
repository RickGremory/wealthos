"""Create goals tables.

Revision ID: 0010_create_goals
Revises: 0009_dashboard_indexes
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0010_create_goals"
down_revision: str | None = "0009_dashboard_indexes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "goals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("target_amount", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("strategy", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_goals_organization_id", "goals", ["organization_id"])
    op.create_index(
        "ix_goals_organization_id_status",
        "goals",
        ["organization_id", "status"],
    )

    op.create_table(
        "goal_accounts",
        sa.Column("goal_id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("goal_id", "account_id"),
    )
    op.create_index("ix_goal_accounts_account_id", "goal_accounts", ["account_id"])

    op.create_table(
        "goal_manual_progress",
        sa.Column("goal_id", sa.Uuid(), nullable=False),
        sa.Column("current_amount", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("goal_id"),
    )


def downgrade() -> None:
    op.drop_table("goal_manual_progress")
    op.drop_index("ix_goal_accounts_account_id", table_name="goal_accounts")
    op.drop_table("goal_accounts")
    op.drop_index("ix_goals_organization_id_status", table_name="goals")
    op.drop_index("ix_goals_organization_id", table_name="goals")
    op.drop_table("goals")
