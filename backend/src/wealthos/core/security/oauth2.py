"""OAuth2 / JWT wiring."""

from __future__ import annotations

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
