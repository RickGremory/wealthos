"""AcceptCashPlanSuggestions command — creates CashPlanItems from suggestions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from wealthos.modules.planning.domain.entities.cash_plan_item import CashPlanItem
from wealthos.modules.planning.domain.exceptions import CashPlanNotFoundError
from wealthos.modules.planning.domain.repositories.cash_plan_item_repository import (
    CashPlanItemRepository,
)
from wealthos.modules.planning.domain.repositories.cash_plan_repository import (
    CashPlanRepository,
)
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class AcceptSuggestionItem:
    item_type: str
    description: str
    expected_date: date
    amount: Decimal
    probability: Decimal = Decimal("100")
    linked_entity_type: str | None = None
    linked_entity_id: UUID | None = None
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class AcceptCashPlanSuggestionsInput:
    organization_id: UUID
    cash_plan_id: UUID
    suggestions: tuple[AcceptSuggestionItem, ...]


class AcceptCashPlanSuggestionsCommand:
    def __init__(
        self,
        cash_plans: CashPlanRepository,
        items: CashPlanItemRepository,
    ) -> None:
        self._cash_plans = cash_plans
        self._items = items

    def execute(self, data: AcceptCashPlanSuggestionsInput) -> list[CashPlanItem]:
        plan = self._cash_plans.get_by_id(data.organization_id, data.cash_plan_id)
        if plan is None:
            raise CashPlanNotFoundError("Cash plan not found.")
        plan.ensure_editable()

        created: list[CashPlanItem] = []
        currency = plan.currency.value
        for suggestion in data.suggestions:
            item = CashPlanItem.create(
                organization_id=data.organization_id,
                cash_plan_id=data.cash_plan_id,
                item_type=suggestion.item_type,
                description=suggestion.description,
                expected_date=suggestion.expected_date,
                amount=Money(suggestion.amount, currency),
                probability=suggestion.probability,
                linked_entity_type=suggestion.linked_entity_type,
                linked_entity_id=suggestion.linked_entity_id,
                notes=suggestion.notes,
            )
            created.append(self._items.add(item))
        return created
