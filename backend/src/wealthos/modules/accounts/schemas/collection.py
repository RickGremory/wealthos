"""Account collection schema."""

from __future__ import annotations

from pydantic import BaseModel

from wealthos.modules.accounts.schemas.response import AccountResponse


class AccountListResponse(BaseModel):
    items: list[AccountResponse]
    total: int
