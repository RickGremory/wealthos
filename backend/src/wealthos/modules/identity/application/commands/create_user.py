"""CreateUser command (internal / tests). Prefer RegisterUser for public signup."""

from __future__ import annotations

from dataclasses import dataclass

from wealthos.modules.identity.application.services.password_hasher import PasswordHasher
from wealthos.modules.identity.application.services.password_policy import validate_password
from wealthos.modules.identity.domain.entities.user import User
from wealthos.modules.identity.domain.exceptions import UserEmailAlreadyExists
from wealthos.modules.identity.domain.repositories.user_repository import UserRepository
from wealthos.modules.identity.domain.value_objects.email import Email


@dataclass(frozen=True, slots=True)
class CreateUserInput:
    email: str
    display_name: str
    password: str


class CreateUserCommand:
    """Create a user with a password hash through the repository port."""

    def __init__(
        self,
        repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._repository = repository
        self._password_hasher = password_hasher

    def execute(self, data: CreateUserInput) -> User:
        email = Email(data.email)
        password = validate_password(data.password)
        if self._repository.get_by_email(email) is not None:
            raise UserEmailAlreadyExists(f"Email '{email.value}' is already registered.")

        user = User.create(email=data.email, display_name=data.display_name)
        return self._repository.add(
            user,
            password_hash=self._password_hasher.hash(password),
        )
