"""CreateUser application tests with in-memory repository."""

from __future__ import annotations

from uuid import UUID

import pytest

from wealthos.modules.identity.application.commands.create_user import (
    CreateUserCommand,
    CreateUserInput,
)
from wealthos.modules.identity.domain.entities.user import User
from wealthos.modules.identity.domain.exceptions import UserEmailAlreadyExists
from wealthos.modules.identity.domain.value_objects.email import Email


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, User] = {}
        self._by_email: dict[str, User] = {}

    def add(self, user: User) -> User:
        self._by_id[user.id] = user
        self._by_email[user.email.value] = user
        return user

    def get_by_id(self, user_id: UUID) -> User | None:
        return self._by_id.get(user_id)

    def get_by_email(self, email: Email) -> User | None:
        return self._by_email.get(email.value)


def test_create_user() -> None:
    command = CreateUserCommand(InMemoryUserRepository())
    user = command.execute(
        CreateUserInput(email="ricardo@example.com", display_name="Ricardo Balam")
    )
    assert user.email.value == "ricardo@example.com"


def test_create_user_rejects_duplicate_email() -> None:
    command = CreateUserCommand(InMemoryUserRepository())
    command.execute(CreateUserInput(email="a@example.com", display_name="One"))
    with pytest.raises(UserEmailAlreadyExists):
        command.execute(CreateUserInput(email="A@example.com", display_name="Two"))
