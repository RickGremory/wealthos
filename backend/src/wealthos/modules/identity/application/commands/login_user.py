"""LoginUser command."""

from __future__ import annotations

from dataclasses import dataclass

from wealthos.modules.identity.application.services.access_token_service import (
    AccessTokenService,
)
from wealthos.modules.identity.application.services.password_hasher import PasswordHasher
from wealthos.modules.identity.domain.entities.user import User
from wealthos.modules.identity.domain.exceptions import (
    InactiveUser,
    InvalidCredentials,
)
from wealthos.modules.identity.domain.repositories.user_repository import UserRepository
from wealthos.modules.identity.domain.value_objects.email import Email


@dataclass(frozen=True, slots=True)
class LoginUserInput:
    email: str
    password: str


@dataclass(frozen=True, slots=True)
class LoginUserResult:
    user: User
    access_token: str
    expires_in: int


class LoginUserCommand:
    """Authenticate a user and issue an access token."""

    def __init__(
        self,
        *,
        users: UserRepository,
        password_hasher: PasswordHasher,
        token_service: AccessTokenService,
    ) -> None:
        self._users = users
        self._password_hasher = password_hasher
        self._token_service = token_service

    def execute(self, data: LoginUserInput) -> LoginUserResult:
        try:
            email = Email(data.email)
        except Exception as exc:
            raise InvalidCredentials("Invalid email or password.") from exc

        user = self._users.get_by_email(email)
        if user is None:
            raise InvalidCredentials("Invalid email or password.")

        if not user.is_active:
            raise InactiveUser("User account is inactive.")

        password_hash = self._users.get_password_hash(user.id)
        if password_hash is None or not self._password_hasher.verify(
            data.password,
            password_hash,
        ):
            raise InvalidCredentials("Invalid email or password.")

        access_token = self._token_service.create(user.id)
        return LoginUserResult(
            user=user,
            access_token=access_token,
            expires_in=self._token_service.expires_in_seconds,
        )
