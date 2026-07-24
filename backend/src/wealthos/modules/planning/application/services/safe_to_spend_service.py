"""Safe-to-spend metric from liquid balance and resolved commitments."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

_ZERO = Decimal("0.00")
_CENT = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class SafeToSpendResult:
    safe_to_spend: Decimal
    funding_gap: Decimal
    liquid_balance: Decimal
    committed_outflows: Decimal
    tax_reserve_shortfall: Decimal
    minimum_cash_buffer: Decimal


class SafeToSpendService:
    """safe = max(0, liquid - committed - tax_shortfall - buffer).

    Caller must pass already-deduped committed_outflows and tax_reserve_shortfall
    (via PlanningCommitmentResolver) to avoid double-counting.
    """

    def calculate(
        self,
        *,
        liquid_balance: Decimal,
        committed_outflows: Decimal,
        tax_reserve_shortfall: Decimal,
        minimum_cash_buffer: Decimal,
    ) -> SafeToSpendResult:
        liquid = _money(liquid_balance)
        committed = _money(committed_outflows)
        tax_shortfall = _money(tax_reserve_shortfall)
        buffer = _money(minimum_cash_buffer)

        reserved = committed + tax_shortfall + buffer
        raw = liquid - reserved
        safe = _money(raw) if raw > _ZERO else _ZERO
        gap = _money(reserved - liquid) if reserved > liquid else _ZERO

        return SafeToSpendResult(
            safe_to_spend=safe,
            funding_gap=gap,
            liquid_balance=liquid,
            committed_outflows=committed,
            tax_reserve_shortfall=tax_shortfall,
            minimum_cash_buffer=buffer,
        )


def _money(value: Decimal | int | str) -> Decimal:
    return Decimal(str(value)).quantize(_CENT, rounding=ROUND_HALF_UP)
