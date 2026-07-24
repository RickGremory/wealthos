"""Budget request/response schemas."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from wealthos.modules.planning.domain.entities.budget import Budget
from wealthos.modules.planning.schemas.allocation import BudgetAllocationResponse

PeriodTypeLiteral = Literal["monthly", "quarterly", "annual", "custom"]
RolloverLiteral = Literal["none", "positive_only", "full"]
ForecastLiteral = Literal["linear", "scheduled", "manual"]


class BudgetCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=120)
    period_type: PeriodTypeLiteral
    currency: str = Field(min_length=3, max_length=3)
    rollover_policy: RolloverLiteral = "none"
    forecast_method: ForecastLiteral = "linear"
    reference_date: date | None = None
    date_from: date | None = None
    date_to: date | None = None


class BudgetUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=2, max_length=120)
    date_from: date | None = None
    date_to: date | None = None
    rollover_policy: RolloverLiteral | None = None
    forecast_method: ForecastLiteral | None = None

    @model_validator(mode="after")
    def reject_empty(self) -> BudgetUpdate:
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self


class BudgetResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    period_type: str
    date_from: date
    date_to: date
    currency: str
    status: str
    rollover_policy: str
    forecast_method: str
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None
    archived_at: datetime | None
    allocations: list[BudgetAllocationResponse] = []

    @classmethod
    def from_entity(
        cls,
        budget: Budget,
        allocations: list[BudgetAllocationResponse] | None = None,
    ) -> BudgetResponse:
        return cls(
            id=budget.id,
            organization_id=budget.organization_id,
            name=budget.name.value,
            period_type=budget.period_type.value,
            date_from=budget.date_from,
            date_to=budget.date_to,
            currency=budget.currency.value,
            status=budget.status.value,
            rollover_policy=budget.rollover_policy.value,
            forecast_method=budget.forecast_method.value,
            created_at=budget.created_at,
            updated_at=budget.updated_at,
            closed_at=budget.closed_at,
            archived_at=budget.archived_at,
            allocations=allocations or [],
        )


class BudgetListResponse(BaseModel):
    items: list[BudgetResponse]
    total: int
