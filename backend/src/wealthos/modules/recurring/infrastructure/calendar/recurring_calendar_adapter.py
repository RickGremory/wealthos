"""Calendar events from Recurring open occurrences (SPEC-005 PR6)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from wealthos.modules.recurring.application.services.occurrence_projector import (
    RecurringOccurrenceProjector,
)
from wealthos.modules.recurring.domain.enums.occurrence import RecurringOccurrenceStatus
from wealthos.modules.recurring.domain.ports.repositories import (
    RecurringAggregateRepository,
    RecurringSettlementRepository,
)


@dataclass(frozen=True, slots=True)
class RecurringCalendarEvent:
    id: str
    recurring_rule_id: UUID
    name: str
    event_type: str  # recurring_occurrence
    event_date: date
    severity: str  # normal | attention | overdue
    currency: str
    direction: str
    amount: Decimal
    occurrence_key: str
    status: str


@dataclass(frozen=True, slots=True)
class RecurringCalendarResult:
    items: tuple[RecurringCalendarEvent, ...]


class RecurringCalendarAdapter:
    """Same generator path as Planning — calendar is a presentation slice."""

    def __init__(
        self,
        repo: RecurringAggregateRepository,
        settlements: RecurringSettlementRepository | None = None,
        projector: RecurringOccurrenceProjector | None = None,
    ) -> None:
        self._projector = projector or RecurringOccurrenceProjector(repo, settlements)

    def collect(
        self,
        organization_id: UUID,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        today: date | None = None,
        timezone: str = "UTC",
        currency: str | None = None,
    ) -> RecurringCalendarResult:
        today = today or date.today()
        date_from = date_from or today
        date_to = date_to or (today + timedelta(days=60))

        projected = self._projector.project(
            organization_id=organization_id,
            period_start=date_from,
            period_end=date_to,
            evaluated_on=today,
            timezone=timezone,
            currency=currency,
            include_externally_managed=False,
            include_transfers=True,
        )
        events = [
            RecurringCalendarEvent(
                id=item.occurrence_key,
                recurring_rule_id=item.occurrence.recurring_rule_id,
                name=item.name,
                event_type="recurring_occurrence",
                event_date=item.occurrence.expected_on,
                severity=_severity(item.status, today=today, expected_on=item.occurrence.expected_on),
                currency=item.occurrence.currency,
                direction=item.direction.value,
                amount=item.outstanding_amount,
                occurrence_key=item.occurrence_key,
                status=item.status.value,
            )
            for item in projected
        ]
        return RecurringCalendarResult(items=tuple(events))


def _severity(
    status: RecurringOccurrenceStatus,
    *,
    today: date,
    expected_on: date,
) -> str:
    if status is RecurringOccurrenceStatus.OVERDUE:
        return "overdue"
    if status is RecurringOccurrenceStatus.DUE or (expected_on - today).days <= 7:
        return "attention"
    return "normal"
