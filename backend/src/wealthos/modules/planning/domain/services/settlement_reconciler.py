"""Reduce outstanding amounts with posted facts (§15, run after dedupe)."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal

from wealthos.modules.planning.domain.enums.cash_flow import CashFlowStatus
from wealthos.modules.planning.domain.value_objects.cash_flow import PlanningCashFlow
from wealthos.modules.planning.domain.value_objects.money_utils import ZERO, quantize_money
from wealthos.modules.planning.domain.value_objects.settlement import PlanningSettlement


@dataclass(frozen=True, slots=True)
class ReconciliationResult:
    cash_flows: tuple[PlanningCashFlow, ...]
    matched_settlements: int
    unmatched_settlements: int


class PlanningSettlementReconciler:
    """Match on ``occurrence_key`` only — amount/date guessing is a warning, not a match."""

    def reconcile(
        self,
        cash_flows: Iterable[PlanningCashFlow],
        settlements: Iterable[PlanningSettlement],
    ) -> ReconciliationResult:
        settled_by_key: dict[str, Decimal] = {}
        unkeyed = 0
        for settlement in settlements:
            key = settlement.source_occurrence_key
            if not key:
                unkeyed += 1
                continue
            settled_by_key[key] = settled_by_key.get(key, ZERO) + abs(settlement.amount)

        matched = 0
        reconciled: list[PlanningCashFlow] = []
        for flow in cash_flows:
            settled = settled_by_key.get(flow.occurrence_key)
            if settled is None:
                reconciled.append(flow)
                continue

            matched += 1
            remaining = quantize_money(flow.outstanding_amount - settled)
            if remaining <= ZERO:
                # Overpayment excess stays in the ledger; it is not a planning inflow.
                reconciled.append(
                    flow.with_outstanding(ZERO, status=CashFlowStatus.SETTLED)
                )
            else:
                reconciled.append(
                    flow.with_outstanding(remaining, status=CashFlowStatus.PARTIALLY_SETTLED)
                )

        return ReconciliationResult(
            cash_flows=tuple(reconciled),
            matched_settlements=matched,
            unmatched_settlements=unkeyed + max(len(settled_by_key) - matched, 0),
        )
