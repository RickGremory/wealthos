"""Create timeline_events for Financial Timeline projection.

Revision ID: 0019_create_timeline_events
Revises: 0018_org_debt_strategy
Create Date: 2026-07-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0019_create_timeline_events"
down_revision: str | None = "0018_org_debt_strategy"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "timeline_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_type", sa.String(length=40), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("importance", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("resource_type", sa.String(length=40), nullable=False),
        sa.Column("resource_id", sa.Uuid(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("amount", sa.Numeric(precision=19, scale=4), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "source_type",
            "event_type",
            "resource_id",
            "occurred_at",
            name="uq_timeline_events_idempotency",
        ),
    )
    op.create_index(
        "ix_timeline_events_org_occurred_at",
        "timeline_events",
        ["organization_id", "occurred_at"],
    )
    op.create_index(
        "ix_timeline_events_org_source_occurred_at",
        "timeline_events",
        ["organization_id", "source_type", "occurred_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_timeline_events_org_source_occurred_at",
        table_name="timeline_events",
    )
    op.drop_index("ix_timeline_events_org_occurred_at", table_name="timeline_events")
    op.drop_table("timeline_events")
