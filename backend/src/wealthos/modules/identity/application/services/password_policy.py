"""Password policy helpers."""

from __future__ import annotations

from wealthos.modules.identity.domain.exceptions import WeakPassword

MIN_PASSWORD_LENGTH = 8


def validate_password(plain_password: str) -> str:
    """Validate and return the plain password (not hashed)."""
    if len(plain_password) < MIN_PASSWORD_LENGTH:
        raise WeakPassword(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")
    return plain_password
