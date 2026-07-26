"""Debt aggregate — liability contract terms (balance lives on Account)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.debts.domain.exceptions import (
    DebtAlreadyArchived,
    DebtAlreadyClosed,
    DebtAlreadyPaused,
    DebtNotPaused,
    InvalidCalendarDay,
    InvalidPaymentAmount,
)
from wealthos.modules.debts.domain.value_objects.debt_name import DebtName
from wealthos.modules.debts.domain.value_objects.debt_priority import DebtPriority
from wealthos.modules.debts.domain.value_objects.debt_status import DebtStatus
from wealthos.modules.debts.domain.value_objects.debt_type import DebtType
from wealthos.modules.debts.domain.value_objects.interest_rate import InterestRate
from wealthos.shared.domain.value_objects.money import Money


def _validate_calendar_day(value: int | None, field: str) -> int | None:
    if value is None:
        return None
    if value < 1 or value > 31:
        raise InvalidCalendarDay(f"{field} must be between 1 and 31.")
    return value


def _ensure_same_currency(
    money: Money | None,
    currency: str,
    field: str,
) -> Money | None:
    if money is None:
        return None
    if money.currency.value != currency:
        raise InvalidPaymentAmount(f"{field} currency must match debt currency.")
    if money.amount < 0:
        raise InvalidPaymentAmount(f"{field} cannot be negative.")
    return money


@dataclass(slots=True)
class Debt:
    id: UUID
    organization_id: UUID
    account_id: UUID
    name: DebtName
    debt_type: DebtType
    creditor: str | None
    currency: str
    priority: DebtPriority
    interest_rate: InterestRate | None
    minimum_payment: Money | None
    scheduled_payment: Money | None
    credit_limit: Money | None
    original_amount: Money | None
    statement_day: int | None
    due_day: int | None
    maturity_date: date | None
    status: DebtStatus
    notes: str | None
    version: int
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None
    archived_at: datetime | None

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        account_id: UUID,
        name: str,
        debt_type: str,
        currency: str,
        creditor: str | None = None,
        priority: str = "medium",
        interest_rate: Decimal | str | int | None = None,
        minimum_payment: Money | None = None,
        scheduled_payment: Money | None = None,
        credit_limit: Money | None = None,
        original_amount: Money | None = None,
        statement_day: int | None = None,
        due_day: int | None = None,
        maturity_date: date | None = None,
        notes: str | None = None,
        debt_id: UUID | None = None,
    ) -> Debt:
        currency_code = currency.strip().upper()
        if len(currency_code) != 3:
            raise InvalidPaymentAmount("Currency must be a 3-letter ISO code.")

        min_payment = _ensure_same_currency(minimum_payment, currency_code, "minimum_payment")
        scheduled = _ensure_same_currency(
            scheduled_payment, currency_code, "scheduled_payment"
        )
        limit = _ensure_same_currency(credit_limit, currency_code, "credit_limit")
        original = _ensure_same_currency(original_amount, currency_code, "original_amount")

        if min_payment is not None and min_payment.amount == 0:
            raise InvalidPaymentAmount("Minimum payment must be positive when set.")
        if scheduled is not None and scheduled.amount == 0:
            raise InvalidPaymentAmount("Scheduled payment must be positive when set.")

        rate = InterestRate(interest_rate) if interest_rate is not None else None
        creditor_clean = creditor.strip() if creditor and creditor.strip() else None

        now = datetime.now(UTC)
        return cls(
            id=debt_id or uuid4(),
            organization_id=organization_id,
            account_id=account_id,
            name=DebtName(name),
            debt_type=DebtType(debt_type),
            creditor=creditor_clean,
            currency=currency_code,
            priority=DebtPriority(priority),
            interest_rate=rate,
            minimum_payment=min_payment,
            scheduled_payment=scheduled,
            credit_limit=limit,
            original_amount=original,
            statement_day=_validate_calendar_day(statement_day, "statement_day"),
            due_day=_validate_calendar_day(due_day, "due_day"),
            maturity_date=maturity_date,
            status=DebtStatus("active"),
            notes=notes.strip() if notes else None,
            version=1,
            created_at=now,
            updated_at=now,
            closed_at=None,
            archived_at=None,
        )

    def rename(self, name: str) -> None:
        self._ensure_mutable()
        self.name = DebtName(name)
        self._touch()

    def change_creditor(self, creditor: str | None) -> None:
        self._ensure_mutable()
        self.creditor = creditor.strip() if creditor and creditor.strip() else None
        self._touch()

    def change_priority(self, priority: str) -> None:
        self._ensure_mutable()
        self.priority = DebtPriority(priority)
        self._touch()

    def change_interest_rate(self, interest_rate: Decimal | str | int | None) -> None:
        self._ensure_mutable()
        self.interest_rate = (
            InterestRate(interest_rate) if interest_rate is not None else None
        )
        self._touch()

    def change_minimum_payment(self, amount: Money | None) -> None:
        self._ensure_mutable()
        if amount is not None:
            if amount.currency.value != self.currency:
                raise InvalidPaymentAmount("Minimum payment currency cannot change.")
            if amount.amount <= 0:
                raise InvalidPaymentAmount("Minimum payment must be positive when set.")
        self.minimum_payment = amount
        self._touch()

    def change_scheduled_payment(self, amount: Money | None) -> None:
        self._ensure_mutable()
        if amount is not None:
            if amount.currency.value != self.currency:
                raise InvalidPaymentAmount("Scheduled payment currency cannot change.")
            if amount.amount <= 0:
                raise InvalidPaymentAmount("Scheduled payment must be positive when set.")
        self.scheduled_payment = amount
        self._touch()

    def change_credit_limit(self, amount: Money | None) -> None:
        self._ensure_mutable()
        if amount is not None:
            if amount.currency.value != self.currency:
                raise InvalidPaymentAmount("Credit limit currency cannot change.")
            if amount.amount < 0:
                raise InvalidPaymentAmount("Credit limit cannot be negative.")
        self.credit_limit = amount
        self._touch()

    def change_maturity_date(self, maturity_date: date | None) -> None:
        self._ensure_mutable()
        self.maturity_date = maturity_date
        self._touch()

    def change_due_day(self, due_day: int | None) -> None:
        self._ensure_mutable()
        self.due_day = _validate_calendar_day(due_day, "due_day")
        self._touch()

    def change_statement_day(self, statement_day: int | None) -> None:
        self._ensure_mutable()
        self.statement_day = _validate_calendar_day(statement_day, "statement_day")
        self._touch()

    def change_notes(self, notes: str | None) -> None:
        self._ensure_mutable()
        self.notes = notes.strip() if notes else None
        self._touch()

    def pause(self) -> None:
        self._ensure_not_archived()
        if self.status.is_closed:
            raise DebtAlreadyClosed("Cannot pause a closed debt.")
        if self.status.is_paused:
            raise DebtAlreadyPaused("Debt is already paused.")
        self.status = DebtStatus("paused")
        self._touch()

    def resume(self) -> None:
        self._ensure_not_archived()
        if not self.status.is_paused:
            raise DebtNotPaused("Debt is not paused.")
        self.status = DebtStatus("active")
        self._touch()

    def close(self) -> None:
        """Mark the financial product as closed (no longer accepts charges)."""
        self._ensure_not_archived()
        if self.status.is_closed:
            raise DebtAlreadyClosed("Debt is already closed.")
        now = datetime.now(UTC)
        self.status = DebtStatus("closed")
        self.closed_at = now
        self.updated_at = now
        self.version += 1

    def archive(self) -> None:
        if self.status.is_archived:
            raise DebtAlreadyArchived("Debt is already archived.")
        now = datetime.now(UTC)
        self.status = DebtStatus("archived")
        self.archived_at = now
        self.updated_at = now
        self.version += 1

    def ensure_accepts_payment(self) -> None:
        if self.status.is_archived:
            raise DebtAlreadyArchived("Cannot pay an archived debt.")
        if self.status.is_closed:
            raise DebtAlreadyClosed("Cannot pay a closed debt.")
        if self.status.is_paused:
            raise DebtAlreadyPaused("Cannot pay a paused debt.")

    def _ensure_mutable(self) -> None:
        self._ensure_not_archived()
        if self.status.is_closed:
            raise DebtAlreadyClosed("Cannot update a closed debt.")

    def _ensure_not_archived(self) -> None:
        if self.status.is_archived:
            raise DebtAlreadyArchived("Cannot update an archived debt.")

    def _touch(self) -> None:
        self.updated_at = datetime.now(UTC)
        self.version += 1
