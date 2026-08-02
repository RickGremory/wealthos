"""Application DTOs for Recurring queries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RecurringOccurrenceDTO:
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
    exception_type: str | None
    name: str
    account_id: UUID | None
    destination_account_id: UUID | None
    category_id: UUID | None
    actual_amount: str | None
    variance_amount: str | None
    can_confirm: bool
    can_skip: bool
    can_reschedule: bool


@dataclass(frozen=True, slots=True)
class RecurringVersionDTO:
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
    days_of_week: tuple[int, ...]
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


@dataclass(frozen=True, slots=True)
class RecurringRuleListDTO:
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
    next_occurrence: RecurringOccurrenceDTO | None


@dataclass(frozen=True, slots=True)
class RecurringRuleDetailDTO:
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
    current_version: RecurringVersionDTO
    versions: tuple[RecurringVersionDTO, ...]
    upcoming_occurrences: tuple[RecurringOccurrenceDTO, ...]
    notes: str | None


@dataclass(frozen=True, slots=True)
class RecurringPreviewDTO:
    dates: tuple[date, ...]
    occurrences: tuple[RecurringOccurrenceDTO, ...]
