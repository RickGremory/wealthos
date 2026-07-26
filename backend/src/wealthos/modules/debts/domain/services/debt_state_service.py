"""Derived commitment display status and calendar day resolution."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

from wealthos.modules.debts.domain.entities.debt import Debt

_ZERO = Decimal("0.00")
_DUE_SOON_DAYS = 7


class CommitmentDisplayStatus(StrEnum):
    ACTIVE = "active"
    DUE_SOON = "due_soon"
    OVERDUE = "overdue"
    SETTLED = "settled"
    PAID_OFF = "paid_off"
    PAUSED = "paused"
    DEFAULTED = "defaulted"
    ARCHIVED = "archived"


def resolve_calendar_day(year: int, month: int, day: int) -> date:
    """Map due_day/statement_day onto a real calendar date (31 → last day)."""
    if day < 1 or day > 31:
        raise ValueError("day must be between 1 and 31.")
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(day, last_day))


def _add_month(year: int, month: int) -> tuple[int, int]:
    if month == 12:
        return year + 1, 1
    return year, month + 1


def next_due_date_on_or_after(*, due_day: int, on_or_after: date) -> date:
    """Next occurrence of due_day on or after the given date."""
    candidate = resolve_calendar_day(on_or_after.year, on_or_after.month, due_day)
    if candidate >= on_or_after:
        return candidate
    year, month = _add_month(on_or_after.year, on_or_after.month)
    return resolve_calendar_day(year, month, due_day)


@dataclass(frozen=True, slots=True)
class DebtStateSnapshot:
    display_status: CommitmentDisplayStatus
    behavior: str
    owed_balance: Decimal
    next_due_date: date | None
    days_until_due: int | None


class DebtStateService:
    """Derive CommitmentDisplayStatus from persisted debt + account balance."""

    def snapshot(
        self,
        debt: Debt,
        *,
        account_balance: Decimal,
        today: date | None = None,
        due_soon_days: int = _DUE_SOON_DAYS,
    ) -> DebtStateSnapshot:
        today = today or date.today()
        owed = abs(account_balance) if account_balance < _ZERO else _ZERO

        next_due: date | None = None
        days_until: int | None = None
        cycle_due: date | None = None
        if debt.due_day is not None:
            cycle_due = resolve_calendar_day(today.year, today.month, debt.due_day)
            if owed > 0:
                if cycle_due < today:
                    year, month = _add_month(today.year, today.month)
                    next_due = resolve_calendar_day(year, month, debt.due_day)
                else:
                    next_due = cycle_due
                days_until = (next_due - today).days

        display = self.display_status(
            debt,
            owed_balance=owed,
            cycle_due_date=cycle_due,
            today=today,
            due_soon_days=due_soon_days,
        )
        return DebtStateSnapshot(
            display_status=display,
            behavior=debt.debt_type.behavior,
            owed_balance=owed,
            next_due_date=next_due,
            days_until_due=days_until,
        )

    def display_status(
        self,
        debt: Debt,
        *,
        owed_balance: Decimal,
        cycle_due_date: date | None = None,
        today: date | None = None,
        due_soon_days: int = _DUE_SOON_DAYS,
    ) -> CommitmentDisplayStatus:
        today = today or date.today()

        if debt.status.is_archived or debt.archived_at is not None:
            return CommitmentDisplayStatus.ARCHIVED
        if debt.status.is_defaulted:
            return CommitmentDisplayStatus.DEFAULTED
        if debt.status.is_paused:
            return CommitmentDisplayStatus.PAUSED

        if owed_balance > 0 and cycle_due_date is not None:
            if cycle_due_date < today:
                return CommitmentDisplayStatus.OVERDUE
            if (cycle_due_date - today).days <= due_soon_days:
                return CommitmentDisplayStatus.DUE_SOON

        if owed_balance == 0:
            if debt.status.is_closed or debt.closed_at is not None:
                return CommitmentDisplayStatus.PAID_OFF
            if debt.debt_type.is_revolving:
                return CommitmentDisplayStatus.SETTLED
            return CommitmentDisplayStatus.ACTIVE

        return CommitmentDisplayStatus.ACTIVE
