"""Budget allocation schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from wealthos.modules.planning.domain.entities.budget_allocation import BudgetAllocation
from wealthos.modules.planning.domain.entities.budget_allocation_match import (
    BudgetAllocationMatch,
)

AllocationTypeLiteral = Literal[
    "income",
    "expense",
    "savings",
    "tax_reserve",
    "debt_payment",
    "goal_contribution",
    "unallocated",
]


class BudgetAllocationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    allocation_type: AllocationTypeLiteral
    amount: Decimal = Field(gt=0)
    category_id: UUID | None = None
    goal_id: UUID | None = None
    debt_id: UUID | None = None
    tax_profile_id: UUID | None = None
    destination_account_id: UUID | None = None
    notes: str | None = Field(default=None, max_length=2000)


class BudgetAllocationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    amount: Decimal | None = Field(default=None, gt=0)
    notes: str | None = Field(default=None, max_length=2000)
    category_id: UUID | None = None
    goal_id: UUID | None = None
    debt_id: UUID | None = None
    tax_profile_id: UUID | None = None
    destination_account_id: UUID | None = None

    @model_validator(mode="after")
    def reject_empty(self) -> BudgetAllocationUpdate:
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self


class BudgetAllocationMatchCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_id: UUID
    matched_amount: Decimal = Field(gt=0)


class BudgetAllocationResponse(BaseModel):
    id: UUID
    organization_id: UUID
    budget_id: UUID
    allocation_type: str
    category_id: UUID | None
    goal_id: UUID | None
    debt_id: UUID | None
    tax_profile_id: UUID | None
    destination_account_id: UUID | None
    amount: Decimal
    currency: str
    notes: str | None
    created_at: datetime
    updated_at: datetime

    @field_serializer("amount")
    def serialize_amount(self, value: Decimal) -> str:
        return format(value, "f")

    @classmethod
    def from_entity(cls, allocation: BudgetAllocation) -> BudgetAllocationResponse:
        return cls(
            id=allocation.id,
            organization_id=allocation.organization_id,
            budget_id=allocation.budget_id,
            allocation_type=allocation.allocation_type.value,
            category_id=allocation.category_id,
            goal_id=allocation.goal_id,
            debt_id=allocation.debt_id,
            tax_profile_id=allocation.tax_profile_id,
            destination_account_id=allocation.destination_account_id,
            amount=allocation.amount.amount,
            currency=allocation.amount.currency.value,
            notes=allocation.notes,
            created_at=allocation.created_at,
            updated_at=allocation.updated_at,
        )


class BudgetAllocationMatchResponse(BaseModel):
    id: UUID
    organization_id: UUID
    budget_allocation_id: UUID
    transaction_id: UUID
    matched_amount: Decimal
    currency: str
    created_at: datetime

    @field_serializer("matched_amount")
    def serialize_amount(self, value: Decimal) -> str:
        return format(value, "f")

    @classmethod
    def from_entity(cls, match: BudgetAllocationMatch) -> BudgetAllocationMatchResponse:
        return cls(
            id=match.id,
            organization_id=match.organization_id,
            budget_allocation_id=match.budget_allocation_id,
            transaction_id=match.transaction_id,
            matched_amount=match.matched_amount.amount,
            currency=match.matched_amount.currency.value,
            created_at=match.created_at,
        )
