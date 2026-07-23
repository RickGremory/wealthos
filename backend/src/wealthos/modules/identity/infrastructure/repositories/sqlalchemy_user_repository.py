"""SQLAlchemy implementation of UserRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.identity.domain.entities.user import User
from wealthos.modules.identity.domain.value_objects.email import Email
from wealthos.modules.identity.infrastructure.mappers.user_mapper import UserMapper
from wealthos.modules.identity.infrastructure.models.user_model import UserModel
from wealthos.shared.base import BaseRepository


class SqlAlchemyUserRepository(BaseRepository[UserModel]):
    """Persist users through SQLAlchemy sessions."""

    def __init__(self, session: Session, mapper: UserMapper | None = None) -> None:
        super().__init__(session, UserModel)
        self._mapper = mapper or UserMapper()

    def add(self, user: User) -> User:
        model = self._mapper.to_model(user)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get_by_id(self, user_id: UUID) -> User | None:
        model = super().get_by_id(user_id)
        if model is None:
            return None
        return self._mapper.to_entity(model)

    def get_by_email(self, email: Email) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email.value)
        model = self.session.scalars(stmt).first()
        if model is None:
            return None
        return self._mapper.to_entity(model)
