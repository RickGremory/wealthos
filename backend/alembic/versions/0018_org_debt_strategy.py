"""Add organization.debt_strategy for commitment payment preferences.

Revision ID: 0018_org_debt_strategy
Revises: 0017_align_debts_commitments
Create Date: 2026-07-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0018_org_debt_strategy"
down_revision: str | None = "0017_align_debts_commitments"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column(
            "debt_strategy",
            sa.String(length=20),
            nullable=False,
            server_default="avalanche",
        ),
    )
    op.alter_column("organizations", "debt_strategy", server_default=None)


def downgrade() -> None:
    op.drop_column("organizations", "debt_strategy")
