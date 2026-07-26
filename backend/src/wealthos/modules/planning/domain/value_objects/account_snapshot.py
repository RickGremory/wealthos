"""Liquidity photograph consumed by the projection engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class PlanningAccountSnapshot:
    """One account's contribution to today's usable cash.

    ``available_balance`` equals ``ledger_balance`` until per-account holds
    exist; the split is kept so the interface survives that change.
    """

    account_id: UUID
    organization_id: UUID
    name: str
    account_type: str
    currency: str
    ledger_balance: Decimal
    available_balance: Decimal
    is_liquid: bool
    is_included: bool
    exclusion_reason: str | None
    balance_as_of: datetime
