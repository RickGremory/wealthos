"""Certainty gates: uncertain income never inflates Safe To Spend (SPEC-004 §9)."""

from __future__ import annotations

from dataclasses import dataclass

from wealthos.modules.planning.domain.enums.alert import PlanningExclusionReason
from wealthos.modules.planning.domain.enums.cash_flow import (
    CashFlowCertainty,
    CashFlowDirection,
)
from wealthos.modules.planning.domain.value_objects.cash_flow import PlanningCashFlow
from wealthos.modules.planning.domain.value_objects.money_utils import ZERO
from wealthos.modules.planning.domain.value_objects.projection_result import ProjectionPeriod


@dataclass(frozen=True, slots=True)
class InclusionDecision:
    included: bool
    reason_code: str | None = None


_INCLUDED = InclusionDecision(included=True)


class IncomeInclusionPolicy:
    """Confirmed always; expected by setting; estimated never in V1."""

    def __init__(self, *, include_expected_income: bool) -> None:
        self._include_expected = include_expected_income

    def decide(self, flow: PlanningCashFlow) -> InclusionDecision:
        if flow.certainty is CashFlowCertainty.CONFIRMED:
            return _INCLUDED
        if flow.certainty is CashFlowCertainty.EXPECTED:
            if self._include_expected:
                return _INCLUDED
            return InclusionDecision(
                included=False,
                reason_code=PlanningExclusionReason.EXPECTED_INCOME_DISABLED.value,
            )
        return InclusionDecision(
            included=False,
            reason_code=PlanningExclusionReason.ESTIMATED_INCOME_EXCLUDED.value,
        )


class ExpenseInclusionPolicy:
    """Probable outflows reduce spendable money — prudence over optimism."""

    def __init__(self, *, include_estimated_expenses: bool) -> None:
        self._include_estimated = include_estimated_expenses

    def decide(self, flow: PlanningCashFlow) -> InclusionDecision:
        if flow.certainty is CashFlowCertainty.ESTIMATED and not self._include_estimated:
            return InclusionDecision(
                included=False,
                reason_code=PlanningExclusionReason.ESTIMATED_EXPENSES_DISABLED.value,
            )
        return _INCLUDED


class CashFlowInclusionPolicy:
    """Composes lifecycle, horizon, currency and certainty gates."""

    def __init__(
        self,
        *,
        include_expected_income: bool,
        include_estimated_expenses: bool,
    ) -> None:
        self.income = IncomeInclusionPolicy(include_expected_income=include_expected_income)
        self.expense = ExpenseInclusionPolicy(
            include_estimated_expenses=include_estimated_expenses
        )

    def decide(
        self,
        flow: PlanningCashFlow,
        *,
        period: ProjectionPeriod,
        currency: str,
    ) -> InclusionDecision:
        if flow.currency.strip().upper() != currency.strip().upper():
            return InclusionDecision(
                included=False,
                reason_code=PlanningExclusionReason.CURRENCY_MISMATCH.value,
            )
        if not flow.status.affects_projection:
            reason = (
                PlanningExclusionReason.CANCELLED.value
                if flow.status.value == "cancelled"
                else PlanningExclusionReason.ALREADY_SETTLED.value
            )
            return InclusionDecision(included=False, reason_code=reason)
        if flow.outstanding_amount <= ZERO:
            return InclusionDecision(
                included=False,
                reason_code=PlanningExclusionReason.ALREADY_SETTLED.value,
            )
        if not period.contains(flow.expected_at):
            return InclusionDecision(
                included=False,
                reason_code=PlanningExclusionReason.OUTSIDE_HORIZON.value,
            )
        if flow.direction is CashFlowDirection.INFLOW:
            return self.income.decide(flow)
        return self.expense.decide(flow)
