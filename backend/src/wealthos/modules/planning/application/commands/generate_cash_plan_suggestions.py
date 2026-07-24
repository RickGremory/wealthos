"""GenerateCashPlanSuggestions command (returns DTOs, does not persist)."""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository
from wealthos.modules.planning.domain.exceptions import CashPlanNotFoundError
from wealthos.modules.planning.domain.repositories.cash_plan_repository import (
    CashPlanRepository,
)
from wealthos.modules.taxes.application.queries.get_tax_summary import GetTaxSummaryQuery


@dataclass(frozen=True, slots=True)
class CashPlanSuggestion:
    item_type: str
    description: str
    expected_date: date
    amount: Decimal
    probability: Decimal
    linked_entity_type: str | None
    linked_entity_id: UUID | None
    source: str
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class GenerateCashPlanSuggestionsInput:
    organization_id: UUID
    cash_plan_id: UUID


class GenerateCashPlanSuggestionsCommand:
    def __init__(
        self,
        cash_plans: CashPlanRepository,
        debts: DebtRepository,
        tax_summary: GetTaxSummaryQuery | None = None,
    ) -> None:
        self._cash_plans = cash_plans
        self._debts = debts
        self._tax_summary = tax_summary

    def execute(self, data: GenerateCashPlanSuggestionsInput) -> list[CashPlanSuggestion]:
        plan = self._cash_plans.get_by_id(data.organization_id, data.cash_plan_id)
        if plan is None:
            raise CashPlanNotFoundError("Cash plan not found.")

        currency = plan.currency.value
        suggestions: list[CashPlanSuggestion] = []

        debts = self._debts.list_by_organization(
            data.organization_id,
            status="active",
            currency=currency,
            include_archived=False,
        )
        for debt in debts:
            if debt.payment_day is None:
                continue
            for due in _payment_dates_in_horizon(plan.date_from, plan.date_to, debt.payment_day):
                suggestions.append(
                    CashPlanSuggestion(
                        item_type="outflow",
                        description=f"Pago mínimo — {debt.name.value}",
                        expected_date=due,
                        amount=debt.minimum_payment.amount,
                        probability=Decimal("100"),
                        linked_entity_type="debt",
                        linked_entity_id=debt.id,
                        source="debt",
                        notes=f"Sugerido desde deuda activa (payment_day={debt.payment_day}).",
                    )
                )

        if self._tax_summary is not None:
            summary = self._tax_summary.execute(data.organization_id)
            for row in summary.by_currency:
                if row.currency != currency:
                    continue
                if row.balance <= Decimal("0.00"):
                    continue
                suggestions.append(
                    CashPlanSuggestion(
                        item_type="outflow",
                        description="Reserva / saldo fiscal estimado",
                        expected_date=plan.date_from,
                        amount=row.balance,
                        probability=Decimal("80"),
                        linked_entity_type="tax_period",
                        linked_entity_id=summary.current_period_id,
                        source="tax",
                        notes="Sugerido desde resumen fiscal (balance due).",
                    )
                )

        return suggestions


def _payment_dates_in_horizon(date_from: date, date_to: date, payment_day: int) -> list[date]:
    dates: list[date] = []
    year, month = date_from.year, date_from.month
    while True:
        last_day = monthrange(year, month)[1]
        day = min(payment_day, last_day)
        candidate = date(year, month, day)
        if candidate > date_to:
            break
        if candidate >= date_from:
            dates.append(candidate)
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        # safety for very long horizons
        if len(dates) > 120:
            break
    return dates
