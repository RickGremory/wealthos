"""Debt payoff plan response schema."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from wealthos.modules.debts.application.services.debt_strategy_simulator import (
    StrategyPlanResult,
)


class PayoffPlanDebtResponse(BaseModel):
    debt_id: UUID
    name: str
    priority: int
    estimated_payoff_date: date | None
    is_payment_sufficient: bool


class PayoffPlanResponse(BaseModel):
    strategy: str
    currency: str
    extra_monthly_payment: Decimal
    estimated_payoff_date: date | None
    months_remaining: int | None
    estimated_total_interest: Decimal | None
    is_payment_sufficient: bool
    debts: list[PayoffPlanDebtResponse]

    @classmethod
    def from_result(cls, result: StrategyPlanResult) -> PayoffPlanResponse:
        return cls(
            strategy=result.strategy,
            currency=result.currency,
            extra_monthly_payment=result.extra_monthly_payment,
            estimated_payoff_date=result.estimated_payoff_date,
            months_remaining=result.months_remaining,
            estimated_total_interest=result.estimated_total_interest,
            is_payment_sufficient=result.is_payment_sufficient,
            debts=[
                PayoffPlanDebtResponse(
                    debt_id=item.debt_id,
                    name=item.name,
                    priority=item.priority,
                    estimated_payoff_date=item.estimated_payoff_date,
                    is_payment_sufficient=item.is_payment_sufficient,
                )
                for item in result.debts
            ],
        )


class PayoffPlanListResponse(BaseModel):
    items: list[PayoffPlanResponse]

    @classmethod
    def from_results(cls, results: list[StrategyPlanResult]) -> PayoffPlanListResponse:
        return cls(items=[PayoffPlanResponse.from_result(result) for result in results])
