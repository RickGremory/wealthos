"""Pydantic schemas for Recurring API."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class DailyPatternSchema(BaseModel):
    frequency: Literal["daily"]
    interval: int = Field(ge=1, default=1)


class WeeklyPatternSchema(BaseModel):
    frequency: Literal["weekly"]
    interval: int = Field(ge=1, default=1)
    days_of_week: list[int] = Field(min_length=1)


class MonthlyPatternSchema(BaseModel):
    frequency: Literal["monthly"]
    interval: int = Field(ge=1, default=1)
    day_of_month: int | None = Field(default=None, ge=1, le=31)
    end_of_month: bool = False
    invalid_date_policy: Literal["last_day_of_month", "skip_occurrence"] = (
        "last_day_of_month"
    )

    @model_validator(mode="after")
    def _day_choice(self) -> MonthlyPatternSchema:
        if self.end_of_month == (self.day_of_month is not None):
            raise ValueError("Provide exactly one of day_of_month or end_of_month.")
        return self


class YearlyPatternSchema(BaseModel):
    frequency: Literal["yearly"]
    interval: int = Field(ge=1, default=1)
    month_of_year: int = Field(ge=1, le=12)
    day_of_month: int | None = Field(default=None, ge=1, le=31)
    end_of_month: bool = False
    invalid_date_policy: Literal["last_day_of_month", "skip_occurrence"] = (
        "last_day_of_month"
    )

    @model_validator(mode="after")
    def _day_choice(self) -> YearlyPatternSchema:
        if self.end_of_month == (self.day_of_month is not None):
            raise ValueError("Provide exactly one of day_of_month or end_of_month.")
        return self


RecurrencePatternSchema = Annotated[
    DailyPatternSchema | WeeklyPatternSchema | MonthlyPatternSchema | YearlyPatternSchema,
    Field(discriminator="frequency"),
]


class CreateRecurringRuleRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    direction: Literal["inflow", "outflow", "transfer"]
    amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    pattern: RecurrencePatternSchema
    starts_on: date
    ends_on: date | None = None
    amount_strategy: Literal["fixed", "estimated"] = "fixed"
    certainty: Literal["confirmed", "expected", "estimated"] = "expected"
    settlement_mode: Literal["single_transaction", "cumulative"] = "single_transaction"
    account_id: UUID | None = None
    destination_account_id: UUID | None = None
    category_id: UUID | None = None
    grace_period_days: int = Field(default=0, ge=0)
    notes: str | None = None


class PreviewUnsavedRequest(BaseModel):
    name: str = Field(default="Preview", max_length=120)
    direction: Literal["inflow", "outflow", "transfer"] = "outflow"
    amount: Decimal = Field(default=Decimal("1.00"), gt=0)
    currency: str = Field(default="MXN", min_length=3, max_length=3)
    pattern: RecurrencePatternSchema
    starts_on: date
    ends_on: date | None = None
    from_date: date = Field(alias="from")
    to_date: date = Field(alias="to")
    amount_strategy: Literal["fixed", "estimated"] = "fixed"
    certainty: Literal["confirmed", "expected", "estimated"] = "expected"
    grace_period_days: int = Field(default=0, ge=0)
    timezone: str | None = None

    model_config = {"populate_by_name": True}


class PreviewRuleRequest(BaseModel):
    from_date: date = Field(alias="from")
    to_date: date = Field(alias="to")
    timezone: str | None = None

    model_config = {"populate_by_name": True}


class CreateVersionRequest(BaseModel):
    effective_from: date
    expected_version: int
    name: str = Field(min_length=1, max_length=120)
    direction: Literal["inflow", "outflow", "transfer"]
    amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    pattern: RecurrencePatternSchema
    starts_on: date
    ends_on: date | None = None
    amount_strategy: Literal["fixed", "estimated"] = "fixed"
    certainty: Literal["confirmed", "expected", "estimated"] = "expected"
    settlement_mode: Literal["single_transaction", "cumulative"] = "single_transaction"
    account_id: UUID | None = None
    destination_account_id: UUID | None = None
    category_id: UUID | None = None
    grace_period_days: int = Field(default=0, ge=0)
    notes: str | None = None


class UpdateMetadataRequest(BaseModel):
    expected_version: int
    notes: str | None = None


class PauseRequest(BaseModel):
    starts_on: date
    ends_on: date | None = None
    expected_version: int
    reason: str | None = None


class ResumeRequest(BaseModel):
    resume_on: date
    expected_version: int


class EndRequest(BaseModel):
    ends_on: date
    expected_version: int


class ArchiveRequest(BaseModel):
    expected_version: int


class CreateExceptionRequest(BaseModel):
    occurrence_key: str
    exception_type: Literal["skip", "reschedule", "amount_override", "override"]
    expected_version: int
    replacement_expected_on: date | None = None
    replacement_amount: Decimal | None = None
    replacement_certainty: Literal["confirmed", "expected", "estimated"] | None = None
    reason: str | None = None


class CreateSettlementRequest(BaseModel):
    occurrence_key: str = Field(min_length=10, max_length=120)
    transaction_id: UUID
    link_type: Literal["explicit", "manual", "suggested_confirmed"] = "manual"
    settled_amount: Decimal | None = Field(default=None, gt=0)


class RecurringSettlementResponse(BaseModel):
    id: UUID
    organization_id: UUID
    recurring_rule_id: UUID
    occurrence_key: str
    transaction_id: UUID
    settled_amount: str
    link_type: str
    linked_by: UUID | None
    linked_at: datetime
    voided_at: datetime | None = None


class RecurringOccurrenceResponse(BaseModel):
    occurrence_key: str
    recurring_rule_id: UUID
    original_expected_on: date
    expected_on: date
    expected_at: datetime
    direction: str
    base_amount: str
    expected_amount: str
    currency: str
    certainty: str
    status: str
    is_exception: bool
    exception_type: str | None = None
    name: str
    account_id: UUID | None = None
    destination_account_id: UUID | None = None
    category_id: UUID | None = None
    actual_amount: str | None = None
    variance_amount: str | None = None
    can_confirm: bool
    can_skip: bool
    can_reschedule: bool


class RecurringVersionResponse(BaseModel):
    id: UUID
    effective_from: date
    effective_until: date | None
    name: str
    direction: str
    amount: str
    currency: str
    frequency: str
    interval: int
    day_of_month: int | None
    end_of_month: bool
    days_of_week: list[int]
    month_of_year: int | None
    invalid_date_policy: str
    starts_on: date
    ends_on: date | None
    grace_period_days: int
    amount_strategy: str
    certainty: str
    settlement_mode: str
    account_id: UUID | None
    destination_account_id: UUID | None
    category_id: UUID | None
    notes: str | None


class RecurringRuleListItemResponse(BaseModel):
    id: UUID
    name: str
    direction: str
    amount: str
    currency: str
    status: str
    source_type: str
    is_managed_externally: bool
    frequency: str
    interval: int
    schedule_label: str
    version: int
    next_occurrence: RecurringOccurrenceResponse | None = None


class RecurringRuleDetailResponse(BaseModel):
    id: UUID
    name: str
    direction: str
    amount: str
    currency: str
    status: str
    source_type: str
    is_managed_externally: bool
    related_resource_type: str | None
    related_resource_id: UUID | None
    version: int
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None
    current_version: RecurringVersionResponse
    versions: list[RecurringVersionResponse]
    upcoming_occurrences: list[RecurringOccurrenceResponse]
    notes: str | None


class RecurringPreviewResponse(BaseModel):
    dates: list[date]
    occurrences: list[RecurringOccurrenceResponse]
