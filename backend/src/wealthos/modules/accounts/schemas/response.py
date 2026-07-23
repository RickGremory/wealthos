"""Account response schema."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from wealthos.modules.accounts.domain.entities.account import Account


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    account_type: str
    classification: Literal["asset", "liability"]
    currency: str
    opening_balance: Decimal
    current_balance: Decimal
    institution_name: str | None
    last_four: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None

    @classmethod
    def from_entity(cls, account: Account) -> AccountResponse:
        return cls(
            id=account.id,
            organization_id=account.organization_id,
            name=account.name.value,
            account_type=account.account_type.value,
            classification=account.account_type.classification,  # type: ignore[arg-type]
            currency=account.currency.value,
            opening_balance=account.opening_balance.amount,
            current_balance=account.current_balance.amount,
            institution_name=account.institution_name,
            last_four=account.last_four,
            is_active=account.is_active,
            created_at=account.created_at,
            updated_at=account.updated_at,
            archived_at=account.archived_at,
        )
