"""Budget performance schemas."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, field_serializer

from wealthos.modules.planning.application.services.budget_performance_service import (
    BudgetPerformanceSummary,
)
from wealthos.modules.planning.domain.entities.budget import Budget


class AllocationPerformanceResponse(BaseModel):
    allocation_id: UUID
    allocation_type: str
    planned_amount: Decimal
    actual_amount: Decimal
    variance_amount: Decimal
    utilization_percentage: Decimal | None
    status: str

    @field_serializer(
        "planned_amount",
        "actual_amount",
        "variance_amount",
        "utilization_percentage",
    )
    def serialize_money(self, value: Decimal | None) -> str | None:
        if value is None:
            return None
        return format(value, "f")


class PaceResponse(BaseModel):
    elapsed_percentage: Decimal
    spending_percentage: Decimal | None
    pace_variance: Decimal | None
    total_days: int
    elapsed_days: int

    @field_serializer("elapsed_percentage", "spending_percentage", "pace_variance")
    def serialize_money(self, value: Decimal | None) -> str | None:
        if value is None:
            return None
        return format(value, "f")


class BudgetPeriodResponse(BaseModel):
    date_from: date
    date_to: date


class BudgetPerformanceSummaryResponse(BaseModel):
    planned_income: Decimal
    actual_income: Decimal
    income_variance: Decimal
    planned_expenses: Decimal
    actual_expenses: Decimal
    expense_variance: Decimal
    planned_surplus: Decimal
    actual_surplus: Decimal
    surplus_variance: Decimal

    @field_serializer(
        "planned_income",
        "actual_income",
        "income_variance",
        "planned_expenses",
        "actual_expenses",
        "expense_variance",
        "planned_surplus",
        "actual_surplus",
        "surplus_variance",
    )
    def serialize_money(self, value: Decimal) -> str:
        return format(value, "f")


class BudgetPerformanceResponse(BaseModel):
    budget_id: UUID
    currency: str
    period: BudgetPeriodResponse
    summary: BudgetPerformanceSummaryResponse
    allocations: list[AllocationPerformanceResponse]
    pace: PaceResponse | None = None

    @classmethod
    def from_summary(
        cls,
        summary: BudgetPerformanceSummary,
        *,
        budget: Budget,
    ) -> BudgetPerformanceResponse:
        pace = None
        if summary.pace is not None:
            pace = PaceResponse(
                elapsed_percentage=summary.pace.elapsed_percentage,
                spending_percentage=summary.pace.spending_percentage,
                pace_variance=summary.pace.pace_variance,
                total_days=summary.pace.total_days,
                elapsed_days=summary.pace.elapsed_days,
            )
        return cls(
            budget_id=budget.id,
            currency=budget.currency.value,
            period=BudgetPeriodResponse(
                date_from=budget.date_from,
                date_to=budget.date_to,
            ),
            summary=BudgetPerformanceSummaryResponse(
                planned_income=summary.planned_income,
                actual_income=summary.actual_income,
                income_variance=summary.income_variance,
                planned_expenses=summary.planned_expenses,
                actual_expenses=summary.actual_expenses,
                expense_variance=summary.expense_variance,
                planned_surplus=summary.planned_surplus,
                actual_surplus=summary.actual_surplus,
                surplus_variance=summary.surplus_variance,
            ),
            allocations=[
                AllocationPerformanceResponse(
                    allocation_id=row.allocation_id,
                    allocation_type=row.allocation_type,
                    planned_amount=row.planned_amount,
                    actual_amount=row.actual_amount,
                    variance_amount=row.variance_amount,
                    utilization_percentage=row.utilization_percentage,
                    status=row.status,
                )
                for row in summary.allocations
            ],
            pace=pace,
        )
