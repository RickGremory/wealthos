"""Which accounts count as usable cash (SPEC-004 §5–6)."""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

from wealthos.modules.planning.domain.enums.alert import PlanningExclusionReason
from wealthos.modules.planning.domain.value_objects.account_snapshot import (
    PlanningAccountSnapshot,
)
from wealthos.modules.planning.domain.value_objects.money_utils import ZERO, quantize_money

#: Liquid, spendable today. Investments and liabilities never contribute cash.
LIQUID_ACCOUNT_TYPES = frozenset({"checking", "savings", "cash", "digital_wallet"})


class AccountEligibilityPolicy:
    """Safe To Spend uses liquid cash, never net worth."""

    def is_liquid(self, account_type: str) -> bool:
        return account_type.strip().lower() in LIQUID_ACCOUNT_TYPES

    def exclusion_reason(self, *, account_type: str, is_active: bool) -> str | None:
        if not is_active:
            return PlanningExclusionReason.ARCHIVED_ACCOUNT.value
        if not self.is_liquid(account_type):
            return PlanningExclusionReason.NON_LIQUID_ACCOUNT.value
        return None

    def eligible(
        self,
        accounts: Iterable[PlanningAccountSnapshot],
        *,
        currency: str,
    ) -> tuple[PlanningAccountSnapshot, ...]:
        code = currency.strip().upper()
        return tuple(
            account
            for account in accounts
            if account.is_included and account.currency.strip().upper() == code
        )

    def current_available_cash(
        self,
        accounts: Iterable[PlanningAccountSnapshot],
        *,
        currency: str,
    ) -> Decimal:
        """Sum of included balances in a single currency — no FX, ever."""
        total = ZERO
        for account in self.eligible(accounts, currency=currency):
            total += account.available_balance
        return quantize_money(total)
