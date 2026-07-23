"""Current authenticated user dependency."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from wealthos.core.database import get_db
from wealthos.core.security.oauth2 import oauth2_scheme
from wealthos.modules.identity.domain.entities.user import User
from wealthos.modules.identity.domain.exceptions import InvalidAccessToken
from wealthos.modules.identity.infrastructure.repositories import SqlAlchemyUserRepository
from wealthos.modules.identity.infrastructure.security.jwt_access_token_service import (
    JwtAccessTokenService,
)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_db)],
) -> User:
    """Resolve the bearer token into an active User entity."""
    token_service = JwtAccessTokenService()
    users = SqlAlchemyUserRepository(session)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = token_service.decode(token)
    except InvalidAccessToken as exc:
        raise credentials_exception from exc

    user = users.get_by_id(payload.user_id)
    if user is None or not user.is_active:
        raise credentials_exception
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
