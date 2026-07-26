"""GetCommitmentCalendarQuery — projected calendar events for obligations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository
from wealthos.modules.debts.domain.services.debt_state_service import (
    CommitmentDisplayStatus,
    DebtStateService,
    next_due_date_on_or_after,
    resolve_calendar_day,
)

_ZERO = Decimal("0.00")


@dataclass(frozen=True, slots=True)
class CommitmentCalendarEvent:
    id: str
    commitment_id: UUID
    name: str
    event_type: str  # payment_due | statement_date | maturity_date | review_date
    event_date: date
    severity: str  # normal | attention | overdue
    currency: str
    amount: Decimal | None = None


@dataclass(frozen=True, slots=True)
class CommitmentCalendarResult:
    items: tuple[CommitmentCalendarEvent, ...]


class GetCommitmentCalendarQuery:
    def __init__(
        self,
        debts: DebtRepository,
        accounts: AccountRepository,
        state_service: DebtStateService | None = None,
    ) -> None:
        self._debts = debts
        self._accounts = accounts
        self._state = state_service or DebtStateService()

    def execute(
        self,
        organization_id: UUID,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        today: date | None = None,
    ) -> CommitmentCalendarResult:
        today = today or date.today()
        date_from = date_from or today
        date_to = date_to or (today + timedelta(days=60))

        events: list[CommitmentCalendarEvent] = []
        debts = self._debts.list_by_organization(organization_id, include_archived=False)

        for debt in debts:
            if debt.status.is_archived:
                continue
            account = self._accounts.get_by_id(organization_id, debt.account_id)
            raw = account.current_balance.amount if account is not None else _ZERO
            snap = self._state.snapshot(debt, account_balance=raw, today=today)
            amount = None
            if debt.scheduled_payment is not None:
                amount = debt.scheduled_payment.amount
            elif debt.minimum_payment is not None:
                amount = debt.minimum_payment.amount

            if debt.due_day is not None and snap.owed_balance > _ZERO:
                due = next_due_date_on_or_after(due_day=debt.due_day, on_or_after=date_from)
                # Walk months in range
                cursor = due
                while cursor <= date_to:
                    severity = "normal"
                    if snap.display_status == CommitmentDisplayStatus.OVERDUE and cursor == due:
                        severity = "overdue"
                    elif (cursor - today).days <= 7:
                        severity = "attention"
                    events.append(
                        CommitmentCalendarEvent(
                            id=f"{debt.id}:payment_due:{cursor.isoformat()}",
                            commitment_id=debt.id,
                            name=debt.name.value,
                            event_type="payment_due",
                            event_date=cursor,
                            severity=severity,
                            currency=debt.currency,
                            amount=amount,
                        )
                    )
                    year = cursor.year + (1 if cursor.month == 12 else 0)
                    month = 1 if cursor.month == 12 else cursor.month + 1
                    cursor = resolve_calendar_day(year, month, debt.due_day)

            if debt.statement_day is not None and debt.status.is_active:
                stmt = next_due_date_on_or_after(
                    due_day=debt.statement_day,
                    on_or_after=date_from,
                )
                cursor = stmt
                while cursor <= date_to:
                    events.append(
                        CommitmentCalendarEvent(
                            id=f"{debt.id}:statement_date:{cursor.isoformat()}",
                            commitment_id=debt.id,
                            name=debt.name.value,
                            event_type="statement_date",
                            event_date=cursor,
                            severity="normal",
                            currency=debt.currency,
                        )
                    )
                    year = cursor.year + (1 if cursor.month == 12 else 0)
                    month = 1 if cursor.month == 12 else cursor.month + 1
                    cursor = resolve_calendar_day(year, month, debt.statement_day)

            if (
                debt.maturity_date is not None
                and date_from <= debt.maturity_date <= date_to
            ):
                events.append(
                    CommitmentCalendarEvent(
                        id=f"{debt.id}:maturity_date:{debt.maturity_date.isoformat()}",
                        commitment_id=debt.id,
                        name=debt.name.value,
                        event_type="maturity_date",
                        event_date=debt.maturity_date,
                        severity="attention",
                        currency=debt.currency,
                    )
                )

            if debt.status.is_paused:
                review = today + timedelta(days=14)
                if date_from <= review <= date_to:
                    events.append(
                        CommitmentCalendarEvent(
                            id=f"{debt.id}:review_date:{review.isoformat()}",
                            commitment_id=debt.id,
                            name=debt.name.value,
                            event_type="review_date",
                            event_date=review,
                            severity="attention",
                            currency=debt.currency,
                        )
                    )

        events.sort(key=lambda e: (e.event_date, e.name))
        return CommitmentCalendarResult(items=tuple(events))
