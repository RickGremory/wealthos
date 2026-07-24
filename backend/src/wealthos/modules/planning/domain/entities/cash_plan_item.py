"""CashPlanItem — expected dated cash movement within a plan."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.planning.domain.exceptions import (
    CashPlanItemNotMatchable,
    InvalidCashPlanItemAmount,
    InvalidPercentage,
    InvalidProbability,
    PlanningError,
)
from wealthos.modules.planning.domain.value_objects.cash_plan_item_status import CashPlanItemStatus
from wealthos.modules.planning.domain.value_objects.cash_plan_item_type import CashPlanItemType
from wealthos.modules.planning.domain.value_objects.linked_entity_type import LinkedEntityType
from wealthos.modules.planning.domain.value_objects.percentage import Percentage
from wealthos.shared.domain.value_objects.money import Money


@dataclass(slots=True)
class CashPlanItem:
    id: UUID
    organization_id: UUID
    cash_plan_id: UUID
    item_type: CashPlanItemType
    description: str
    expected_date: date
    amount: Money
    probability: Percentage
    status: CashPlanItemStatus
    category_id: UUID | None
    account_id: UUID | None
    linked_entity_type: LinkedEntityType | None
    linked_entity_id: UUID | None
    recurrence_rule: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    cancelled_at: datetime | None

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        cash_plan_id: UUID,
        item_type: str,
        description: str,
        expected_date: date,
        amount: Money,
        probability: Decimal | str | int = 100,
        status: str = "planned",
        category_id: UUID | None = None,
        account_id: UUID | None = None,
        linked_entity_type: str | None = None,
        linked_entity_id: UUID | None = None,
        recurrence_rule: str | None = None,
        notes: str | None = None,
        item_id: UUID | None = None,
    ) -> CashPlanItem:
        if amount.amount <= Decimal("0.00"):
            raise InvalidCashPlanItemAmount("Cash plan item amount must be positive.")
        try:
            probability_vo = Percentage(probability)
        except InvalidPercentage as exc:
            raise InvalidProbability(str(exc)) from exc

        linked_type = LinkedEntityType(linked_entity_type) if linked_entity_type else None
        if (linked_type is None) ^ (linked_entity_id is None):
            raise PlanningError("Provide both linked_entity_type and linked_entity_id, or neither.")

        now = datetime.now(UTC)
        return cls(
            id=item_id or uuid4(),
            organization_id=organization_id,
            cash_plan_id=cash_plan_id,
            item_type=CashPlanItemType(item_type),
            description=description.strip(),
            expected_date=expected_date,
            amount=amount,
            probability=probability_vo,
            status=CashPlanItemStatus(status),
            category_id=category_id,
            account_id=account_id,
            linked_entity_type=linked_type,
            linked_entity_id=linked_entity_id,
            recurrence_rule=recurrence_rule.strip() if recurrence_rule else None,
            notes=notes.strip() if notes else None,
            created_at=now,
            updated_at=now,
            cancelled_at=None,
        )

    def update(
        self,
        *,
        description: str | None = None,
        expected_date: date | None = None,
        amount: Money | None = None,
        probability: Decimal | str | int | None = None,
        category_id: UUID | None = None,
        account_id: UUID | None = None,
        linked_entity_type: str | None = None,
        linked_entity_id: UUID | None = None,
        recurrence_rule: str | None = None,
        notes: str | None = None,
        status: str | None = None,
        fields_set: frozenset[str] | None = None,
    ) -> None:
        self.ensure_matchable_or_planned()
        touched = fields_set

        if description is not None and (touched is None or "description" in touched):
            self.description = description.strip()
        if expected_date is not None and (touched is None or "expected_date" in touched):
            self.expected_date = expected_date
        if amount is not None and (touched is None or "amount" in touched):
            if amount.amount <= Decimal("0.00"):
                raise InvalidCashPlanItemAmount("Cash plan item amount must be positive.")
            if amount.currency != self.amount.currency:
                raise InvalidCashPlanItemAmount("Cash plan item currency cannot change.")
            self.amount = amount
        if probability is not None and (touched is None or "probability" in touched):
            try:
                self.probability = Percentage(probability)
            except InvalidPercentage as exc:
                raise InvalidProbability(str(exc)) from exc
        if touched is None or "category_id" in touched:
            if category_id is not None or (touched and "category_id" in touched):
                self.category_id = category_id
        if touched is None or "account_id" in touched:
            if account_id is not None or (touched and "account_id" in touched):
                self.account_id = account_id
        if touched is None or "linked_entity_type" in touched or "linked_entity_id" in touched:
            if linked_entity_type is not None or (touched and "linked_entity_type" in touched):
                self.linked_entity_type = (
                    LinkedEntityType(linked_entity_type) if linked_entity_type else None
                )
            if linked_entity_id is not None or (touched and "linked_entity_id" in touched):
                self.linked_entity_id = linked_entity_id
            if (self.linked_entity_type is None) ^ (self.linked_entity_id is None):
                raise PlanningError(
                    "Provide both linked_entity_type and linked_entity_id, or neither."
                )
        if recurrence_rule is not None or (touched and "recurrence_rule" in touched):
            self.recurrence_rule = recurrence_rule.strip() if recurrence_rule else None
        if notes is not None or (touched and "notes" in touched):
            self.notes = notes.strip() if notes else None
        if status is not None and (touched is None or "status" in touched):
            if status in {"matched", "partially_matched", "cancelled"}:
                raise CashPlanItemNotMatchable(
                    "Use dedicated methods to change match/cancel status."
                )
            self.status = CashPlanItemStatus(status)

        self.updated_at = datetime.now(UTC)

    def cancel(self) -> None:
        if self.status.is_cancelled:
            return
        if self.status.is_matched:
            raise CashPlanItemNotMatchable("Cannot cancel a fully matched cash plan item.")
        now = datetime.now(UTC)
        self.status = CashPlanItemStatus("cancelled")
        self.cancelled_at = now
        self.updated_at = now

    def mark_partially_matched(self) -> None:
        self.ensure_matchable()
        self.status = CashPlanItemStatus("partially_matched")
        self.updated_at = datetime.now(UTC)

    def mark_matched(self) -> None:
        self.ensure_matchable()
        self.status = CashPlanItemStatus("matched")
        self.updated_at = datetime.now(UTC)

    def mark_confirmed(self) -> None:
        self.ensure_matchable_or_planned()
        if self.status.is_matched or self.status.is_partially_matched:
            raise CashPlanItemNotMatchable("Cannot confirm an already matched item.")
        self.status = CashPlanItemStatus("confirmed")
        self.updated_at = datetime.now(UTC)

    def mark_overdue(self) -> None:
        if self.status.is_cancelled or self.status.is_matched:
            return
        self.status = CashPlanItemStatus("overdue")
        self.updated_at = datetime.now(UTC)

    def ensure_matchable(self) -> None:
        if not self.status.is_matchable:
            raise CashPlanItemNotMatchable(
                f"Cash plan item with status '{self.status.value}' cannot accept matches."
            )

    def ensure_matchable_or_planned(self) -> None:
        if self.status.is_cancelled:
            raise CashPlanItemNotMatchable("Cannot update a cancelled cash plan item.")
        if self.status.is_matched:
            raise CashPlanItemNotMatchable("Cannot update a fully matched cash plan item.")
