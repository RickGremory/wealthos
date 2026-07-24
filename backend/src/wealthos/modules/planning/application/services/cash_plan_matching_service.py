"""Pure helpers for cash-plan item ↔ transaction matching."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

_ZERO = Decimal("0.00")
_CENT = Decimal("0.01")


class CashPlanMatchingService:
    """remaining_amount / can_match / status transitions for matches."""

    def remaining_amount(
        self,
        *,
        planned_amount: Decimal,
        matched_amount: Decimal,
    ) -> Decimal:
        planned = _money(planned_amount)
        matched = _money(matched_amount)
        remaining = planned - matched
        return remaining if remaining > _ZERO else _ZERO

    def can_match(
        self,
        *,
        planned_amount: Decimal,
        matched_amount: Decimal,
        match_amount: Decimal,
        allow_over: bool = False,
    ) -> bool:
        try:
            self.validate_match_amount(
                planned_amount=planned_amount,
                matched_amount=matched_amount,
                match_amount=match_amount,
                allow_over=allow_over,
            )
        except ValueError:
            return False
        return True

    def validate_match_amount(
        self,
        *,
        planned_amount: Decimal,
        matched_amount: Decimal,
        match_amount: Decimal,
        allow_over: bool = False,
    ) -> Decimal:
        amount = _money(match_amount)
        if amount <= _ZERO:
            raise ValueError("match_amount must be greater than zero")
        remaining = self.remaining_amount(
            planned_amount=planned_amount,
            matched_amount=matched_amount,
        )
        if not allow_over and amount > remaining:
            raise ValueError("match_amount exceeds remaining planned amount")
        return amount

    def new_status(
        self,
        *,
        planned_amount: Decimal,
        matched_amount_after: Decimal,
    ) -> str:
        planned = _money(planned_amount)
        matched = _money(matched_amount_after)
        if matched <= _ZERO:
            return "planned"
        if matched >= planned:
            return "matched"
        return "partially_matched"


def _money(value: Decimal | int | str) -> Decimal:
    return Decimal(str(value)).quantize(_CENT, rounding=ROUND_HALF_UP)
