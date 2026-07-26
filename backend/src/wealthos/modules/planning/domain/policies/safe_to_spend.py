"""Trough-based Safe To Spend (SPEC-004 §17–21)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from wealthos.modules.planning.domain.value_objects.money_utils import ZERO, quantize_money


@dataclass(frozen=True, slots=True)
class SafeToSpendOutcome:
    """``cash_deficit`` is money missing outright; ``reserve_shortfall`` is
    protected money the projection eats into. They never overlap."""

    safe_to_spend: Decimal
    cash_deficit: Decimal | None
    reserve_shortfall: Decimal | None

    @property
    def breaches_reserve(self) -> bool:
        return self.reserve_shortfall is not None or self.cash_deficit is not None


class SafeToSpendPolicy:
    """``max(0, minimum_projected_balance − required_reserve)``.

    Ending balance is irrelevant: spending today must survive the trough.
    """

    def calculate(
        self,
        *,
        minimum_projected_balance: Decimal,
        required_reserve: Decimal,
    ) -> SafeToSpendOutcome:
        minimum = quantize_money(minimum_projected_balance)
        reserve = quantize_money(required_reserve)

        raw = minimum - reserve
        safe = quantize_money(raw) if raw > ZERO else ZERO

        cash_deficit = quantize_money(-minimum) if minimum < ZERO else None

        protected_cash = minimum if minimum > ZERO else ZERO
        shortfall = reserve - protected_cash
        reserve_shortfall = quantize_money(shortfall) if shortfall > ZERO else None

        return SafeToSpendOutcome(
            safe_to_spend=safe,
            cash_deficit=cash_deficit,
            reserve_shortfall=reserve_shortfall,
        )
