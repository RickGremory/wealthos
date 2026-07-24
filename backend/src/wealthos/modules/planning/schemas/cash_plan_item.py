"""Cash plan item schemas."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from wealthos.modules.planning.application.commands.generate_cash_plan_suggestions import (
    CashPlanSuggestion,
)
from wealthos.modules.planning.domain.entities.cash_plan_item import CashPlanItem
from wealthos.modules.planning.domain.entities.cash_plan_item_match import CashPlanItemMatch

ItemTypeLiteral = Literal["inflow", "outflow", "transfer_in", "transfer_out"]
LinkedEntityLiteral = Literal["debt", "tax_period", "goal", "transaction", "invoice", "manual"]


class CashPlanItemCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    item_type: ItemTypeLiteral
    description: str = Field(min_length=1, max_length=240)
    expected_date: date
    amount: Decimal = Field(gt=0)
    probability: Decimal = Field(default=Decimal("100"), ge=0, le=100)
    category_id: UUID | None = None
    account_id: UUID | None = None
    linked_entity_type: LinkedEntityLiteral | None = None
    linked_entity_id: UUID | None = None
    recurrence_rule: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=2000)


class CashPlanItemUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    description: str | None = Field(default=None, min_length=1, max_length=240)
    expected_date: date | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    probability: Decimal | None = Field(default=None, ge=0, le=100)
    category_id: UUID | None = None
    account_id: UUID | None = None
    linked_entity_type: LinkedEntityLiteral | None = None
    linked_entity_id: UUID | None = None
    recurrence_rule: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=2000)
    status: Literal["planned", "confirmed", "overdue"] | None = None

    @model_validator(mode="after")
    def reject_empty(self) -> CashPlanItemUpdate:
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self


class CashPlanItemMatchCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_id: UUID
    matched_amount: Decimal = Field(gt=0)


class CashPlanItemResponse(BaseModel):
    id: UUID
    organization_id: UUID
    cash_plan_id: UUID
    item_type: str
    description: str
    expected_date: date
    amount: Decimal
    currency: str
    probability: Decimal
    status: str
    category_id: UUID | None
    account_id: UUID | None
    linked_entity_type: str | None
    linked_entity_id: UUID | None
    recurrence_rule: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    cancelled_at: datetime | None

    @field_serializer("amount", "probability")
    def serialize_decimal(self, value: Decimal) -> str:
        return format(value, "f")

    @classmethod
    def from_entity(cls, item: CashPlanItem) -> CashPlanItemResponse:
        return cls(
            id=item.id,
            organization_id=item.organization_id,
            cash_plan_id=item.cash_plan_id,
            item_type=item.item_type.value,
            description=item.description,
            expected_date=item.expected_date,
            amount=item.amount.amount,
            currency=item.amount.currency.value,
            probability=item.probability.value,
            status=item.status.value,
            category_id=item.category_id,
            account_id=item.account_id,
            linked_entity_type=(item.linked_entity_type.value if item.linked_entity_type else None),
            linked_entity_id=item.linked_entity_id,
            recurrence_rule=item.recurrence_rule,
            notes=item.notes,
            created_at=item.created_at,
            updated_at=item.updated_at,
            cancelled_at=item.cancelled_at,
        )


class CashPlanItemMatchResponse(BaseModel):
    id: UUID
    organization_id: UUID
    cash_plan_item_id: UUID
    transaction_id: UUID
    matched_amount: Decimal
    currency: str
    created_at: datetime

    @field_serializer("matched_amount")
    def serialize_amount(self, value: Decimal) -> str:
        return format(value, "f")

    @classmethod
    def from_entity(cls, match: CashPlanItemMatch) -> CashPlanItemMatchResponse:
        return cls(
            id=match.id,
            organization_id=match.organization_id,
            cash_plan_item_id=match.cash_plan_item_id,
            transaction_id=match.transaction_id,
            matched_amount=match.matched_amount.amount,
            currency=match.matched_amount.currency.value,
            created_at=match.created_at,
        )


class CashPlanSuggestionResponse(BaseModel):
    item_type: str
    description: str
    expected_date: date
    amount: Decimal
    probability: Decimal
    linked_entity_type: str | None
    linked_entity_id: UUID | None
    source: str
    notes: str | None = None

    @field_serializer("amount", "probability")
    def serialize_decimal(self, value: Decimal) -> str:
        return format(value, "f")

    @classmethod
    def from_suggestion(cls, suggestion: CashPlanSuggestion) -> CashPlanSuggestionResponse:
        return cls(
            item_type=suggestion.item_type,
            description=suggestion.description,
            expected_date=suggestion.expected_date,
            amount=suggestion.amount,
            probability=suggestion.probability,
            linked_entity_type=suggestion.linked_entity_type,
            linked_entity_id=suggestion.linked_entity_id,
            source=suggestion.source,
            notes=suggestion.notes,
        )


class CashPlanSuggestionListResponse(BaseModel):
    items: list[CashPlanSuggestionResponse]
    total: int


class AcceptCashPlanSuggestionsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    suggestions: list[CashPlanSuggestionResponse] = Field(min_length=1)
