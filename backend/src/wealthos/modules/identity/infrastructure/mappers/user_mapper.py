"""Map User ↔ UserModel (password hash stays in persistence)."""

from __future__ import annotations

from wealthos.modules.identity.domain.entities.user import User
from wealthos.modules.identity.domain.value_objects.display_name import DisplayName
from wealthos.modules.identity.domain.value_objects.email import Email
from wealthos.modules.identity.infrastructure.models.user_model import UserModel
from wealthos.shared.base import BaseMapper


class UserMapper(BaseMapper[UserModel, User]):
    """Convert between the SQLAlchemy model and the domain aggregate."""

    def to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=Email(model.email),
            display_name=DisplayName(model.display_name),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def to_model(self, entity: User) -> UserModel:
        raise RuntimeError("Use build_model(entity, password_hash=...) for persistence.")

    def build_model(self, entity: User, *, password_hash: str) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email.value,
            display_name=entity.display_name.value,
            password_hash=password_hash,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
