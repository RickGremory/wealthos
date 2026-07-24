"""Budget forecast schemas."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, field_serializer

from wealthos.modules.planning.application.services.budget_forecast_service import (
    BudgetForecast,
)


class ForecastAllocationResponse(BaseModel):
    allocation_id: UUID
    allocation_type: str
    planned: Decimal
    actual_to_date: Decimal
    projected_at_close: Decimal
    projected_variance: Decimal

    @field_serializer("planned", "actual_to_date", "projected_at_close", "projected_variance")
    def serialize_money(self, value: Decimal) -> str:
        return format(value, "f")


class BudgetForecastResponse(BaseModel):
    projected_income: Decimal
    projected_expenses: Decimal
    projected_surplus: Decimal
    elapsed_days: int
    total_days: int
    allocations: list[ForecastAllocationResponse]

    @field_serializer("projected_income", "projected_expenses", "projected_surplus")
    def serialize_money(self, value: Decimal) -> str:
        return format(value, "f")

    @classmethod
    def from_forecast(cls, forecast: BudgetForecast) -> BudgetForecastResponse:
        return cls(
            projected_income=forecast.projected_income,
            projected_expenses=forecast.projected_expenses,
            projected_surplus=forecast.projected_surplus,
            elapsed_days=forecast.elapsed_days,
            total_days=forecast.total_days,
            allocations=[
                ForecastAllocationResponse(
                    allocation_id=row.allocation_id,
                    allocation_type=row.allocation_type,
                    planned=row.planned,
                    actual_to_date=row.actual_to_date,
                    projected_at_close=row.projected_at_close,
                    projected_variance=row.projected_variance,
                )
                for row in forecast.allocations
            ],
        )
