"""pwdlib Argon2 password hasher."""

from __future__ import annotations

from pwdlib import PasswordHash


class PwdlibPasswordHasher:
    """Argon2id hasher recommended by pwdlib."""

    def __init__(self) -> None:
        self._hasher = PasswordHash.recommended()

    def hash(self, plain_password: str) -> str:
        return self._hasher.hash(plain_password)

    def verify(self, plain_password: str, password_hash: str) -> bool:
        return self._hasher.verify(plain_password, password_hash)
