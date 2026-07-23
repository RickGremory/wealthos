"""ORM models package — import models so Alembic sees Base.metadata."""

from wealthos.modules.identity.infrastructure.models.user_model import UserModel

__all__ = ["UserModel"]
