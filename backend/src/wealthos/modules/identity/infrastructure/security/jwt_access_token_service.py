"""JWT access token service."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from wealthos.core.settings import Settings, get_settings
from wealthos.modules.identity.application.services.access_token_service import (
    AccessTokenPayload,
)
from wealthos.modules.identity.domain.exceptions import InvalidAccessToken


class JwtAccessTokenService:
    """HS256 JWT access tokens with standard claims."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    @property
    def expires_in_seconds(self) -> int:
        return self._settings.auth_access_token_expire_minutes * 60

    def create(self, user_id: UUID) -> str:
        now = datetime.now(UTC)
        expires = now + timedelta(minutes=self._settings.auth_access_token_expire_minutes)
        payload = {
            "sub": str(user_id),
            "iat": now,
            "exp": expires,
            "iss": self._settings.auth_jwt_issuer,
            "aud": self._settings.auth_jwt_audience,
        }
        return jwt.encode(
            payload,
            self._settings.auth_jwt_secret,
            algorithm=self._settings.auth_jwt_algorithm,
        )

    def decode(self, token: str) -> AccessTokenPayload:
        try:
            payload = jwt.decode(
                token,
                self._settings.auth_jwt_secret,
                algorithms=[self._settings.auth_jwt_algorithm],
                audience=self._settings.auth_jwt_audience,
                issuer=self._settings.auth_jwt_issuer,
            )
            user_id = UUID(payload["sub"])
        except (jwt.PyJWTError, KeyError, ValueError, TypeError) as exc:
            raise InvalidAccessToken("Invalid or expired access token.") from exc
        return AccessTokenPayload(user_id=user_id)
