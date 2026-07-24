"""Pure cash projection engine (Decimal money math, no DB)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

_ZERO = Decimal("0.00")
_CENT = Decimal("0.01")
_HUNDRED = Decimal("100")

_INFLOW_TYPES = frozenset({"inflow", "transfer_in"})
_OUTFLOW_TYPES = frozenset({"outflow", "transfer_out"})
_CANCELLED = "cancelled"
_CONFIRMED = "confirmed"
_MATCHED = "matched"
_PARTIALLY_MATCHED = "partially_matched"


@dataclass(frozen=True, slots=True)
class CashProjectionItem:
    item_id: UUID
    item_type: str  # inflow, outflow, transfer_in, transfer_out
    expected_date: date
    amount: Decimal
    probability: Decimal  # 0-100
    status: str
    matched_amount: Decimal  # sum of matches
    matched_dates: tuple[date, ...]  # real dates from matches
    # remaining planned on expected_date if partial


@dataclass(frozen=True, slots=True)
class CashProjectionInput:
    opening_balance: Decimal
    date_from: date
    date_to: date
    items: tuple[CashProjectionItem, ...]
    scenario: str  # committed, expected, optimistic
    included_account_ids: frozenset[UUID] | None = None


@dataclass(frozen=True, slots=True)
class CashProjectionPoint:
    date: date
    inflows: Decimal
    outflows: Decimal
    ending_balance: Decimal
    lowest_intraday_balance: Decimal


@dataclass(frozen=True, slots=True)
class CashProjection:
    points: tuple[CashProjectionPoint, ...]
    ending_balance: Decimal
    minimum_balance: Decimal
    first_shortfall_date: date | None


class CashProjectionService:
    """Project liquidity day-by-day under committed / expected / optimistic scenarios."""

    def project(self, data: CashProjectionInput) -> CashProjection:
        opening = _money(data.opening_balance)
        scenario = data.scenario.strip().lower()

        day_inflows: dict[date, Decimal] = defaultdict(lambda: _ZERO)
        day_outflows: dict[date, Decimal] = defaultdict(lambda: _ZERO)

        for item in data.items:
            if item.status == _CANCELLED:
                continue
            for flow_date, signed_amount in _expand_item_flows(item, scenario):
                if flow_date < data.date_from or flow_date > data.date_to:
                    continue
                if signed_amount > _ZERO:
                    day_inflows[flow_date] += signed_amount
                elif signed_amount < _ZERO:
                    day_outflows[flow_date] += abs(signed_amount)

        points: list[CashProjectionPoint] = []
        balance = opening
        minimum = opening
        first_shortfall: date | None = None if opening >= _ZERO else data.date_from

        cursor = data.date_from
        while cursor <= data.date_to:
            inflows = _money(day_inflows[cursor])
            outflows = _money(day_outflows[cursor])

            # Prudent intraday order: outflows first, then inflows.
            after_outflows = balance - outflows
            lowest = after_outflows
            ending = after_outflows + inflows

            if first_shortfall is None and (after_outflows < _ZERO or ending < _ZERO):
                first_shortfall = cursor

            balance = ending
            if lowest < minimum:
                minimum = lowest
            if ending < minimum:
                minimum = ending

            points.append(
                CashProjectionPoint(
                    date=cursor,
                    inflows=inflows,
                    outflows=outflows,
                    ending_balance=_money(ending),
                    lowest_intraday_balance=_money(lowest),
                )
            )
            cursor += timedelta(days=1)

        return CashProjection(
            points=tuple(points),
            ending_balance=_money(balance),
            minimum_balance=_money(minimum),
            first_shortfall_date=first_shortfall,
        )


def _expand_item_flows(
    item: CashProjectionItem,
    scenario: str,
) -> list[tuple[date, Decimal]]:
    """Return (date, signed_amount) where inflows are positive, outflows negative."""
    amount = _money(item.amount)
    matched = min(_money(item.matched_amount), amount)
    remaining = amount - matched
    is_inflow = item.item_type in _INFLOW_TYPES
    sign = Decimal("1") if is_inflow else Decimal("-1")

    flows: list[tuple[date, Decimal]] = []

    if matched > _ZERO:
        # Matched cash always counts at face value (already happened).
        distributed = _distribute_matched(matched, item.matched_dates, item.expected_date)
        for match_date, match_slice in distributed:
            flows.append((match_date, sign * match_slice))

    if remaining <= _ZERO:
        return flows

    applied = _scenario_amount(
        remaining,
        probability=_money(item.probability),
        status=item.status,
        scenario=scenario,
        is_inflow=is_inflow,
    )
    if applied > _ZERO:
        flows.append((item.expected_date, sign * applied))
    return flows


def _scenario_amount(
    remaining: Decimal,
    *,
    probability: Decimal,
    status: str,
    scenario: str,
    is_inflow: bool,
) -> Decimal:
    if scenario == "optimistic":
        return remaining

    if scenario == "committed":
        if status == _CONFIRMED or probability >= _HUNDRED:
            return remaining
        # Matched/partially_matched remaining is only committed if confirmed or 100%.
        return _ZERO

    # expected
    if is_inflow:
        weight = (probability / _HUNDRED).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        return _money(remaining * weight)
    return remaining


def _distribute_matched(
    matched: Decimal,
    matched_dates: tuple[date, ...],
    fallback: date,
) -> list[tuple[date, Decimal]]:
    if not matched_dates:
        return [(fallback, matched)]
    if len(matched_dates) == 1:
        return [(matched_dates[0], matched)]

    n = len(matched_dates)
    base = (matched / Decimal(n)).quantize(_CENT, rounding=ROUND_HALF_UP)
    slices = [base] * n
    drift = matched - sum(slices)
    slices[-1] = _money(slices[-1] + drift)
    return list(zip(matched_dates, slices, strict=True))


def _money(value: Decimal | int | str) -> Decimal:
    return Decimal(str(value)).quantize(_CENT, rounding=ROUND_HALF_UP)
