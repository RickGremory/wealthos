"""Dashboard slim upcoming + pending confirmation count (SPEC-005 PR6)."""

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
class RecurringDashboardUpcomingItem:
    id: str
    date_label: str
    description: str
    amount: Decimal
    currency: str
    status: str  # normal | attention | overdue
    to: str
    due_in_days: int
    occurrence_key: str


@dataclass(frozen=True, slots=True)
class RecurringDashboardSlice:
    upcoming: tuple[RecurringDashboardUpcomingItem, ...]
    pending_confirmation_count: int


class RecurringDashboardAdapter:
    """Currency-sliced upcoming (3–4) + pending confirmation count."""

    def __init__(
        self,
        repo: RecurringAggregateRepository,
        settlements: RecurringSettlementRepository | None = None,
        projector: RecurringOccurrenceProjector | None = None,
        *,
        limit: int = 4,
        horizon_days: int = 45,
    ) -> None:
        self._projector = projector or RecurringOccurrenceProjector(repo, settlements)
        self._limit = limit
        self._horizon_days = horizon_days

    def collect(
        self,
        organization_id: UUID,
        *,
        currency: str,
        today: date | None = None,
        timezone: str = "UTC",
    ) -> RecurringDashboardSlice:
        today = today or date.today()
        currency = currency.strip().upper()
        projected = self._projector.project(
            organization_id=organization_id,
            period_start=today - timedelta(days=14),
            period_end=today + timedelta(days=self._horizon_days),
            evaluated_on=today,
            timezone=timezone,
            currency=currency,
            include_externally_managed=False,
            include_transfers=False,
        )

        pending = sum(
            1
            for item in projected
            if item.status
            in {
                RecurringOccurrenceStatus.DUE,
                RecurringOccurrenceStatus.OVERDUE,
                RecurringOccurrenceStatus.PARTIALLY_SETTLED,
            }
        )

        upcoming: list[RecurringDashboardUpcomingItem] = []
        for item in projected:
            if len(upcoming) >= self._limit:
                break
            due_in = (item.occurrence.expected_on - today).days
            upcoming.append(
                RecurringDashboardUpcomingItem(
                    id=item.occurrence_key,
                    date_label=_date_label(due_in),
                    description=f"Recurrente · {item.name}",
                    amount=item.outstanding_amount,
                    currency=item.occurrence.currency,
                    status=_status_label(item.status, due_in),
                    to=f"/app/recurring/{item.occurrence.recurring_rule_id}",
                    due_in_days=due_in,
                    occurrence_key=item.occurrence_key,
                )
            )
        return RecurringDashboardSlice(
            upcoming=tuple(upcoming),
            pending_confirmation_count=pending,
        )


def _date_label(due_in_days: int) -> str:
    if due_in_days < 0:
        return f"Hace {abs(due_in_days)} día(s)"
    if due_in_days == 0:
        return "Hoy"
    return f"En {due_in_days} día(s)"


def _status_label(status: RecurringOccurrenceStatus, due_in_days: int) -> str:
    if status is RecurringOccurrenceStatus.OVERDUE or due_in_days < 0:
        return "overdue"
    if status is RecurringOccurrenceStatus.DUE or due_in_days <= 7:
        return "attention"
    return "normal"
