"""Password hasher and JWT token unit tests."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest

from wealthos.core.settings import Settings
from wealthos.modules.identity.domain.exceptions import InvalidAccessToken
from wealthos.modules.identity.infrastructure.security.jwt_access_token_service import (
    JwtAccessTokenService,
)
from wealthos.modules.identity.infrastructure.security.pwdlib_password_hasher import (
    PwdlibPasswordHasher,
)


def test_password_hash_differs_from_plain() -> None:
    hasher = PwdlibPasswordHasher()
    hashed = hasher.hash("WealthOS-2026-Segura")
    assert hashed != "WealthOS-2026-Segura"
    assert hasher.verify("WealthOS-2026-Segura", hashed) is True


def test_password_verify_rejects_wrong_password() -> None:
    hasher = PwdlibPasswordHasher()
    hashed = hasher.hash("WealthOS-2026-Segura")
    assert hasher.verify("wrong-password", hashed) is False


def test_jwt_contains_sub_and_expiry() -> None:
    settings = Settings(
        auth_jwt_secret="test-secret-key-for-jwt-unit-tests",
        auth_access_token_expire_minutes=15,
    )
    service = JwtAccessTokenService(settings)
    user_id = uuid4()
    token = service.create(user_id)
    payload = jwt.decode(
        token,
        settings.auth_jwt_secret,
        algorithms=[settings.auth_jwt_algorithm],
        audience=settings.auth_jwt_audience,
        issuer=settings.auth_jwt_issuer,
    )
    assert payload["sub"] == str(user_id)
    assert "exp" in payload
    assert "iat" in payload
    assert service.decode(token).user_id == user_id


def test_jwt_rejects_expired_token() -> None:
    settings = Settings(auth_jwt_secret="test-secret-key-for-jwt-unit-tests")
    service = JwtAccessTokenService(settings)
    user_id = uuid4()
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": str(user_id),
            "iat": now - timedelta(hours=1),
            "exp": now - timedelta(minutes=1),
            "iss": settings.auth_jwt_issuer,
            "aud": settings.auth_jwt_audience,
        },
        settings.auth_jwt_secret,
        algorithm=settings.auth_jwt_algorithm,
    )
    with pytest.raises(InvalidAccessToken):
        service.decode(token)


def test_jwt_rejects_invalid_signature() -> None:
    settings = Settings(auth_jwt_secret="test-secret-key-for-jwt-unit-tests")
    other = Settings(auth_jwt_secret="another-secret-key-for-jwt-unit-tests")
    token = JwtAccessTokenService(other).create(uuid4())
    with pytest.raises(InvalidAccessToken):
        JwtAccessTokenService(settings).decode(token)
