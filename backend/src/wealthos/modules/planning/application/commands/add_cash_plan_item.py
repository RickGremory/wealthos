"""AddCashPlanItem command."""

from __future__ import annotations

from dataclasses import dataclass
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
    CashPlanNotFoundError,
    InvalidCashPlanDateRange,
)
from wealthos.modules.planning.domain.repositories.cash_plan_item_repository import (
    CashPlanItemRepository,
)
from wealthos.modules.planning.domain.repositories.cash_plan_repository import (
    CashPlanRepository,
)
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class AddCashPlanItemInput:
    organization_id: UUID
    cash_plan_id: UUID
    item_type: str
    description: str
    expected_date: date
    amount: Decimal
    probability: Decimal = Decimal("100")
    category_id: UUID | None = None
    account_id: UUID | None = None
    linked_entity_type: str | None = None
    linked_entity_id: UUID | None = None
    recurrence_rule: str | None = None
    notes: str | None = None


class AddCashPlanItemCommand:
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

    def execute(self, data: AddCashPlanItemInput) -> CashPlanItem:
        plan = self._cash_plans.get_by_id(data.organization_id, data.cash_plan_id)
        if plan is None:
            raise CashPlanNotFoundError("Cash plan not found.")
        plan.ensure_editable()
        if not (plan.date_from <= data.expected_date <= plan.date_to):
            raise InvalidCashPlanDateRange(
                "Cash plan item expected_date must fall within the plan horizon."
            )

        currency = plan.currency.value
        if data.category_id is not None:
            self._validator.ensure_category(data.organization_id, data.category_id)
        if data.account_id is not None:
            self._validator.ensure_account(data.organization_id, data.account_id, currency)
        if data.linked_entity_type == "debt" and data.linked_entity_id is not None:
            self._validator.ensure_debt(data.organization_id, data.linked_entity_id, currency)
        if data.linked_entity_type == "goal" and data.linked_entity_id is not None:
            self._validator.ensure_goal(data.organization_id, data.linked_entity_id, currency)

        item = CashPlanItem.create(
            organization_id=data.organization_id,
            cash_plan_id=data.cash_plan_id,
            item_type=data.item_type,
            description=data.description,
            expected_date=data.expected_date,
            amount=Money(data.amount, currency),
            probability=data.probability,
            category_id=data.category_id,
            account_id=data.account_id,
            linked_entity_type=data.linked_entity_type,
            linked_entity_id=data.linked_entity_id,
            recurrence_rule=data.recurrence_rule,
            notes=data.notes,
        )
        return self._items.add(item)
