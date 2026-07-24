"""Goal create/update schemas."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class GoalCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=120)
    target_amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    strategy: Literal["manual", "linked_accounts", "net_worth_percentage"]
    target_date: date | None = None
    linked_account_ids: list[UUID] = Field(default_factory=list)


class GoalUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=2, max_length=120)
    target_amount: Decimal | None = Field(default=None, gt=0)
    target_date: date | None = None
    linked_account_ids: list[UUID] | None = None

    @model_validator(mode="after")
    def reject_empty(self) -> GoalUpdate:
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self


class ManualProgressUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_amount: Decimal = Field(ge=0)
