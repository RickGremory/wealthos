"""Debt aggregate — liability contract terms (balance lives on Account)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.debts.domain.exceptions import (
    DebtAlreadyArchived,
    DebtAlreadyPaidOff,
    InvalidMinimumPayment,
    InvalidPaymentDay,
)
from wealthos.modules.debts.domain.value_objects.debt_name import DebtName
from wealthos.modules.debts.domain.value_objects.debt_status import DebtStatus
from wealthos.modules.debts.domain.value_objects.debt_type import DebtType
from wealthos.modules.debts.domain.value_objects.interest_rate import InterestRate
from wealthos.shared.domain.value_objects.money import Money


def _validate_calendar_day(value: int | None, field: str) -> int | None:
    if value is None:
        return None
    if value < 1 or value > 31:
        raise InvalidPaymentDay(f"{field} must be between 1 and 31.")
    return value


@dataclass(slots=True)
class Debt:
    id: UUID
    organization_id: UUID
    account_id: UUID
    name: DebtName
    debt_type: DebtType
    annual_interest_rate: InterestRate
    minimum_payment: Money
    original_principal: Money | None
    opened_at: date | None
    maturity_date: date | None
    payment_day: int | None
    statement_day: int | None
    status: DebtStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime
    paid_off_at: datetime | None
    archived_at: datetime | None

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        account_id: UUID,
        name: str,
        debt_type: str,
        annual_interest_rate: Decimal | str | int,
        minimum_payment: Money,
        original_principal: Money | None = None,
        opened_at: date | None = None,
        maturity_date: date | None = None,
        payment_day: int | None = None,
        statement_day: int | None = None,
        notes: str | None = None,
        debt_id: UUID | None = None,
    ) -> Debt:
        if minimum_payment.amount <= Decimal("0.00"):
            raise InvalidMinimumPayment("Minimum payment must be positive.")
        if (
            original_principal is not None
            and original_principal.currency != minimum_payment.currency
        ):
            raise InvalidMinimumPayment(
                "Original principal currency must match minimum payment currency."
            )
        if original_principal is not None and original_principal.amount < 0:
            raise InvalidMinimumPayment("Original principal cannot be negative.")

        now = datetime.now(UTC)
        return cls(
            id=debt_id or uuid4(),
            organization_id=organization_id,
            account_id=account_id,
            name=DebtName(name),
            debt_type=DebtType(debt_type),
            annual_interest_rate=InterestRate(annual_interest_rate),
            minimum_payment=minimum_payment,
            original_principal=original_principal,
            opened_at=opened_at,
            maturity_date=maturity_date,
            payment_day=_validate_calendar_day(payment_day, "payment_day"),
            statement_day=_validate_calendar_day(statement_day, "statement_day"),
            status=DebtStatus("active"),
            notes=notes.strip() if notes else None,
            created_at=now,
            updated_at=now,
            paid_off_at=None,
            archived_at=None,
        )

    def rename(self, name: str) -> None:
        self._ensure_mutable()
        self.name = DebtName(name)
        self.updated_at = datetime.now(UTC)

    def change_interest_rate(self, annual_interest_rate: Decimal | str | int) -> None:
        self._ensure_mutable()
        self.annual_interest_rate = InterestRate(annual_interest_rate)
        self.updated_at = datetime.now(UTC)

    def change_minimum_payment(self, amount: Money) -> None:
        self._ensure_mutable()
        if amount.currency != self.minimum_payment.currency:
            raise InvalidMinimumPayment("Minimum payment currency cannot change.")
        if amount.amount <= Decimal("0.00"):
            raise InvalidMinimumPayment("Minimum payment must be positive.")
        self.minimum_payment = amount
        self.updated_at = datetime.now(UTC)

    def change_maturity_date(self, maturity_date: date | None) -> None:
        self._ensure_mutable()
        self.maturity_date = maturity_date
        self.updated_at = datetime.now(UTC)

    def change_payment_day(self, payment_day: int | None) -> None:
        self._ensure_mutable()
        self.payment_day = _validate_calendar_day(payment_day, "payment_day")
        self.updated_at = datetime.now(UTC)

    def change_statement_day(self, statement_day: int | None) -> None:
        self._ensure_mutable()
        self.statement_day = _validate_calendar_day(statement_day, "statement_day")
        self.updated_at = datetime.now(UTC)

    def change_notes(self, notes: str | None) -> None:
        self._ensure_mutable()
        self.notes = notes.strip() if notes else None
        self.updated_at = datetime.now(UTC)

    def mark_paid_off(self) -> None:
        if self.status.is_archived:
            raise DebtAlreadyArchived("Cannot mark an archived debt as paid off.")
        if self.status.is_paid_off:
            raise DebtAlreadyPaidOff("Debt is already paid off.")
        now = datetime.now(UTC)
        self.status = DebtStatus("paid_off")
        self.paid_off_at = now
        self.updated_at = now

    def archive(self) -> None:
        if self.status.is_archived:
            raise DebtAlreadyArchived("Debt is already archived.")
        now = datetime.now(UTC)
        self.status = DebtStatus("archived")
        self.archived_at = now
        self.updated_at = now

    def ensure_accepts_payment(self) -> None:
        if self.status.is_archived:
            raise DebtAlreadyArchived("Cannot pay an archived debt.")
        if self.status.is_paid_off:
            raise DebtAlreadyPaidOff("Cannot pay a debt that is already paid off.")

    def _ensure_mutable(self) -> None:
        if self.status.is_archived:
            raise DebtAlreadyArchived("Cannot update an archived debt.")
