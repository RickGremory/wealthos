"""Account balance summary views."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AccountBalanceView:
    account_id: UUID
    name: str
    account_type: str
    classification: str
    currency: str
    institution_name: str | None
    current_balance: Decimal
    display_balance: Decimal
    is_active: bool


@dataclass(frozen=True, slots=True)
class AccountBalanceGroupView:
    currency: str
    accounts: tuple[AccountBalanceView, ...]
