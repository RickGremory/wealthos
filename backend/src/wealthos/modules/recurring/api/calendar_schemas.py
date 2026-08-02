"""Calendar event schemas for Recurring."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from wealthos.modules.recurring.infrastructure.calendar.recurring_calendar_adapter import (
    RecurringCalendarResult,
)


class RecurringCalendarEventResponse(BaseModel):
    id: str
    recurring_rule_id: UUID
    name: str
    event_type: str
    event_date: date
    severity: str
    currency: str
    direction: str
    amount: Decimal
    occurrence_key: str
    status: str


class RecurringCalendarEventsResponse(BaseModel):
    items: list[RecurringCalendarEventResponse] = Field(default_factory=list)

    @classmethod
    def from_result(cls, result: RecurringCalendarResult) -> RecurringCalendarEventsResponse:
        return cls(
            items=[
                RecurringCalendarEventResponse(
                    id=item.id,
                    recurring_rule_id=item.recurring_rule_id,
                    name=item.name,
                    event_type=item.event_type,
                    event_date=item.event_date,
                    severity=item.severity,
                    currency=item.currency,
                    direction=item.direction,
                    amount=item.amount,
                    occurrence_key=item.occurrence_key,
                    status=item.status,
                )
                for item in result.items
            ]
        )
