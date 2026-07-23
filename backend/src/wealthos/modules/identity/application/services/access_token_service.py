"""Access token port."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AccessTokenPayload:
    user_id: UUID


class AccessTokenService(Protocol):
    def create(self, user_id: UUID) -> str: ...

    def decode(self, token: str) -> AccessTokenPayload: ...

    @property
    def expires_in_seconds(self) -> int: ...
