"""FastAPI dependencies for the identity module."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from wealthos.core.database import get_db
from wealthos.modules.identity.application.commands.create_user import CreateUserCommand
from wealthos.modules.identity.domain.repositories.user_repository import UserRepository
from wealthos.modules.identity.infrastructure.repositories import SqlAlchemyUserRepository
from wealthos.shared.persistence import SqlAlchemyUnitOfWork


def get_unit_of_work(
    session: Annotated[Session, Depends(get_db)],
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def get_user_repository(
    session: Annotated[Session, Depends(get_db)],
) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def get_create_user_command(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> CreateUserCommand:
    return CreateUserCommand(repository)
