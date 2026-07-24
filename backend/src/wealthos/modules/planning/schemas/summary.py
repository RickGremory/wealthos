"""Planning summary schema."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, field_serializer

from wealthos.modules.planning.application.queries.get_planning_summary import (
    PlanningSummary,
)


class PlanningSummaryResponse(BaseModel):
    active_budgets: int
    draft_budgets: int
    active_cash_plans: int
    draft_cash_plans: int
    currency: str | None
    safe_to_spend: Decimal | None
    funding_gap: Decimal | None
    primary_cash_plan_id: UUID | None

    @field_serializer("safe_to_spend", "funding_gap")
    def serialize_money(self, value: Decimal | None) -> str | None:
        if value is None:
            return None
        return format(value, "f")

    @classmethod
    def from_summary(cls, summary: PlanningSummary) -> PlanningSummaryResponse:
        return cls(
            active_budgets=summary.active_budgets,
            draft_budgets=summary.draft_budgets,
            active_cash_plans=summary.active_cash_plans,
            draft_cash_plans=summary.draft_cash_plans,
            currency=summary.currency,
            safe_to_spend=summary.safe_to_spend,
            funding_gap=summary.funding_gap,
            primary_cash_plan_id=summary.primary_cash_plan_id,
        )
