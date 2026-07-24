"""Cash plan schemas."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from wealthos.modules.planning.domain.entities.cash_plan import CashPlan
from wealthos.modules.planning.schemas.cash_plan_item import CashPlanItemResponse

OpeningBalanceModeLiteral = Literal["current_liquid_balance", "selected_accounts", "manual"]
CashBufferTypeLiteral = Literal[
    "fixed_amount", "days_of_expenses", "percentage_of_monthly_expenses"
]


class CashPlanCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=120)
    date_from: date
    date_to: date
    currency: str = Field(min_length=3, max_length=3)
    opening_balance_mode: OpeningBalanceModeLiteral
    manual_opening_balance: Decimal | None = None
    account_ids: list[UUID] = Field(default_factory=list)
    minimum_cash_buffer_type: CashBufferTypeLiteral = "fixed_amount"
    minimum_cash_buffer_value: Decimal = Field(default=Decimal("0.00"), ge=0)


class CashPlanUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=2, max_length=120)
    date_from: date | None = None
    date_to: date | None = None
    opening_balance_mode: OpeningBalanceModeLiteral | None = None
    manual_opening_balance: Decimal | None = None
    account_ids: list[UUID] | None = None
    minimum_cash_buffer_type: CashBufferTypeLiteral | None = None
    minimum_cash_buffer_value: Decimal | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def reject_empty(self) -> CashPlanUpdate:
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self


class CashPlanResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    date_from: date
    date_to: date
    currency: str
    opening_balance_mode: str
    manual_opening_balance: Decimal | None
    account_ids: list[UUID]
    minimum_cash_buffer_type: str
    minimum_cash_buffer_value: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None
    items: list[CashPlanItemResponse] = []

    @field_serializer("manual_opening_balance", "minimum_cash_buffer_value")
    def serialize_money(self, value: Decimal | None) -> str | None:
        if value is None:
            return None
        return format(value, "f")

    @classmethod
    def from_entity(
        cls,
        plan: CashPlan,
        *,
        account_ids: list[UUID] | None = None,
        items: list[CashPlanItemResponse] | None = None,
    ) -> CashPlanResponse:
        return cls(
            id=plan.id,
            organization_id=plan.organization_id,
            name=plan.name.value,
            date_from=plan.date_from,
            date_to=plan.date_to,
            currency=plan.currency.value,
            opening_balance_mode=plan.opening_balance_mode.value,
            manual_opening_balance=(
                plan.manual_opening_balance.amount if plan.manual_opening_balance else None
            ),
            account_ids=account_ids or [],
            minimum_cash_buffer_type=plan.minimum_cash_buffer_type.value,
            minimum_cash_buffer_value=plan.minimum_cash_buffer_value,
            status=plan.status.value,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
            archived_at=plan.archived_at,
            items=items or [],
        )


class CashPlanListResponse(BaseModel):
    items: list[CashPlanResponse]
    total: int
