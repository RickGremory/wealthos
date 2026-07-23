"""CreateUser command."""

from __future__ import annotations

from dataclasses import dataclass

from wealthos.modules.identity.domain.entities.user import User
from wealthos.modules.identity.domain.exceptions import UserEmailAlreadyExists
from wealthos.modules.identity.domain.repositories.user_repository import UserRepository
from wealthos.modules.identity.domain.value_objects.email import Email


@dataclass(frozen=True, slots=True)
class CreateUserInput:
    email: str
    display_name: str


class CreateUserCommand:
    """Create a user through the repository port."""

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def execute(self, data: CreateUserInput) -> User:
        email = Email(data.email)
        if self._repository.get_by_email(email) is not None:
            raise UserEmailAlreadyExists(f"Email '{email.value}' is already registered.")

        user = User.create(email=data.email, display_name=data.display_name)
        return self._repository.add(user)
