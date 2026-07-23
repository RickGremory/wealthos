"""ORM models package — import models so Alembic sees Base.metadata."""

from wealthos.modules.organizations.infrastructure.models.organization_model import (
    OrganizationModel,
)

__all__ = ["OrganizationModel"]
