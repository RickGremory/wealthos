"""PlannedCashFlow — a user hypothesis about future money (never a Transaction)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.planning.domain.enums.cash_flow import (
    CashFlowCertainty,
    CashFlowDirection,
    CashFlowStatus,
)
from wealthos.modules.planning.domain.exceptions import (
    InvalidPlannedCashFlowAmount,
    PlannedCashFlowNameEmpty,
    PlannedCashFlowNameTooLong,
    PlannedCashFlowNotEditable,
)
from wealthos.shared.domain.value_objects.money import Money

MAX_NAME_LENGTH = 120
MAX_NOTES_LENGTH = 500


@dataclass(slots=True)
class PlannedCashFlow:
    id: UUID
    organization_id: UUID
    name: str
    direction: CashFlowDirection
    amount: Money
    expected_at: datetime
    certainty: CashFlowCertainty
    status: CashFlowStatus
    notes: str | None
    settled_transaction_id: UUID | None
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        name: str,
        direction: str | CashFlowDirection,
        amount: Money,
        expected_at: datetime,
        certainty: str | CashFlowCertainty = CashFlowCertainty.EXPECTED,
        notes: str | None = None,
        cash_flow_id: UUID | None = None,
    ) -> PlannedCashFlow:
        if amount.amount <= Decimal("0.00"):
            raise InvalidPlannedCashFlowAmount("Planned cash flow amount must be positive.")

        now = datetime.now(UTC)
        return cls(
            id=cash_flow_id or uuid4(),
            organization_id=organization_id,
            name=_clean_name(name),
            direction=CashFlowDirection.parse(direction),
            amount=amount,
            expected_at=_ensure_aware(expected_at),
            certainty=CashFlowCertainty.parse(certainty),
            status=CashFlowStatus.ACTIVE,
            notes=_clean_notes(notes),
            settled_transaction_id=None,
            version=1,
            created_at=now,
            updated_at=now,
        )

    @property
    def occurrence_key(self) -> str:
        return f"planned:{self.id}"

    def update(
        self,
        *,
        name: str | None = None,
        direction: str | CashFlowDirection | None = None,
        amount: Money | None = None,
        expected_at: datetime | None = None,
        certainty: str | CashFlowCertainty | None = None,
        notes: str | None = None,
        fields_set: frozenset[str] | None = None,
    ) -> None:
        self._ensure_editable()
        touched = fields_set

        def is_set(field: str) -> bool:
            return touched is None or field in touched

        if name is not None and is_set("name"):
            self.name = _clean_name(name)
        if direction is not None and is_set("direction"):
            self.direction = CashFlowDirection.parse(direction)
        if amount is not None and is_set("amount"):
            if amount.amount <= Decimal("0.00"):
                raise InvalidPlannedCashFlowAmount("Planned cash flow amount must be positive.")
            if amount.currency != self.amount.currency:
                raise InvalidPlannedCashFlowAmount("Planned cash flow currency cannot change.")
            self.amount = amount
        if expected_at is not None and is_set("expected_at"):
            self.expected_at = _ensure_aware(expected_at)
        if certainty is not None and is_set("certainty"):
            self.certainty = CashFlowCertainty.parse(certainty)
        if is_set("notes"):
            self.notes = _clean_notes(notes)

        self.bump_version()

    def cancel(self) -> None:
        if self.status is CashFlowStatus.CANCELLED:
            return
        self._ensure_editable()
        self.status = CashFlowStatus.CANCELLED
        self.bump_version()

    def settle(self, transaction_id: UUID) -> None:
        self._ensure_editable()
        self.status = CashFlowStatus.SETTLED
        self.settled_transaction_id = transaction_id
        self.bump_version()

    def expire(self) -> None:
        self._ensure_editable()
        self.status = CashFlowStatus.EXPIRED
        self.bump_version()

    def _ensure_editable(self) -> None:
        if self.status is CashFlowStatus.SETTLED:
            raise PlannedCashFlowNotEditable("Cannot modify a settled planned cash flow.")
        if self.status is CashFlowStatus.CANCELLED:
            raise PlannedCashFlowNotEditable("Cannot modify a cancelled planned cash flow.")

    def bump_version(self) -> None:
        self.updated_at = datetime.now(UTC)
        self.version += 1


def _clean_name(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise PlannedCashFlowNameEmpty("Planned cash flow name cannot be empty.")
    if len(cleaned) > MAX_NAME_LENGTH:
        raise PlannedCashFlowNameTooLong(
            f"Planned cash flow name cannot exceed {MAX_NAME_LENGTH} characters."
        )
    return cleaned


def _clean_notes(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned[:MAX_NOTES_LENGTH] or None


def _ensure_aware(value: datetime) -> datetime:
    """Planning compares instants; naive input is read as UTC."""
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)
