"""UpdateCashPlanItem command."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.categories.domain.repositories.category_repository import (
    CategoryRepository,
)
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository
from wealthos.modules.goals.domain.repositories.goal_repository import GoalRepository
from wealthos.modules.planning.application.commands._linked_resource_validator import (
    LinkedResourceValidator,
)
from wealthos.modules.planning.domain.entities.cash_plan_item import CashPlanItem
from wealthos.modules.planning.domain.exceptions import (
    CashPlanItemNotFoundError,
    CashPlanNotFoundError,
)
from wealthos.modules.planning.domain.repositories.cash_plan_item_repository import (
    CashPlanItemRepository,
)
from wealthos.modules.planning.domain.repositories.cash_plan_repository import (
    CashPlanRepository,
)
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class UpdateCashPlanItemInput:
    organization_id: UUID
    cash_plan_id: UUID
    item_id: UUID
    description: str | None = None
    expected_date: date | None = None
    amount: Decimal | None = None
    probability: Decimal | None = None
    category_id: UUID | None = None
    account_id: UUID | None = None
    linked_entity_type: str | None = None
    linked_entity_id: UUID | None = None
    recurrence_rule: str | None = None
    notes: str | None = None
    status: str | None = None
    fields_set: frozenset[str] = field(default_factory=frozenset)


class UpdateCashPlanItemCommand:
    def __init__(
        self,
        cash_plans: CashPlanRepository,
        items: CashPlanItemRepository,
        accounts: AccountRepository,
        categories: CategoryRepository,
        goals: GoalRepository,
        debts: DebtRepository,
    ) -> None:
        self._cash_plans = cash_plans
        self._items = items
        self._validator = LinkedResourceValidator(
            accounts=accounts,
            categories=categories,
            goals=goals,
            debts=debts,
        )

    def execute(self, data: UpdateCashPlanItemInput) -> CashPlanItem:
        plan = self._cash_plans.get_by_id(data.organization_id, data.cash_plan_id)
        if plan is None:
            raise CashPlanNotFoundError("Cash plan not found.")
        plan.ensure_editable()

        item = self._items.get_by_id(data.organization_id, data.item_id)
        if item is None or item.cash_plan_id != data.cash_plan_id:
            raise CashPlanItemNotFoundError("Cash plan item not found.")

        currency = plan.currency.value
        if "category_id" in data.fields_set and data.category_id is not None:
            self._validator.ensure_category(data.organization_id, data.category_id)
        if "account_id" in data.fields_set and data.account_id is not None:
            self._validator.ensure_account(data.organization_id, data.account_id, currency)

        linked_type = (
            data.linked_entity_type
            if "linked_entity_type" in data.fields_set
            else (item.linked_entity_type.value if item.linked_entity_type else None)
        )
        linked_id = (
            data.linked_entity_id
            if "linked_entity_id" in data.fields_set
            else item.linked_entity_id
        )
        if linked_type == "debt" and linked_id is not None:
            self._validator.ensure_debt(data.organization_id, linked_id, currency)
        if linked_type == "goal" and linked_id is not None:
            self._validator.ensure_goal(data.organization_id, linked_id, currency)

        amount = None
        if "amount" in data.fields_set and data.amount is not None:
            amount = Money(data.amount, currency)

        item.update(
            description=data.description,
            expected_date=data.expected_date,
            amount=amount,
            probability=data.probability,
            category_id=data.category_id,
            account_id=data.account_id,
            linked_entity_type=data.linked_entity_type,
            linked_entity_id=data.linked_entity_id,
            recurrence_rule=data.recurrence_rule,
            notes=data.notes,
            status=data.status,
            fields_set=data.fields_set,
        )
        return self._items.save(item)
