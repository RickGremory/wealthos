"""CreateCashPlan command."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.planning.application.commands._linked_resource_validator import (
    LinkedResourceValidator,
)
from wealthos.modules.planning.domain.entities.cash_plan import CashPlan
from wealthos.modules.planning.domain.exceptions import SelectedAccountsRequired
from wealthos.modules.planning.domain.repositories.cash_plan_repository import (
    CashPlanRepository,
)
from wealthos.modules.planning.domain.value_objects.opening_balance_mode import (
    OpeningBalanceMode,
)
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class CreateCashPlanInput:
    organization_id: UUID
    name: str
    date_from: date
    date_to: date
    currency: str
    opening_balance_mode: str
    manual_opening_balance: Decimal | None = None
    account_ids: tuple[UUID, ...] = ()
    minimum_cash_buffer_type: str = "fixed_amount"
    minimum_cash_buffer_value: Decimal = Decimal("0.00")


class CreateCashPlanCommand:
    def __init__(
        self,
        cash_plans: CashPlanRepository,
        accounts: AccountRepository,
    ) -> None:
        self._cash_plans = cash_plans
        self._validator = LinkedResourceValidator(accounts=accounts)

    def execute(self, data: CreateCashPlanInput) -> CashPlan:
        mode = OpeningBalanceMode(data.opening_balance_mode)
        if mode.is_selected_accounts and not data.account_ids:
            raise SelectedAccountsRequired(
                "selected_accounts opening balance mode requires account_ids."
            )

        for account_id in data.account_ids:
            self._validator.ensure_account(data.organization_id, account_id, data.currency)

        manual = None
        if data.manual_opening_balance is not None:
            manual = Money(data.manual_opening_balance, data.currency)

        plan = CashPlan.create(
            organization_id=data.organization_id,
            name=data.name,
            date_from=data.date_from,
            date_to=data.date_to,
            currency=data.currency,
            opening_balance_mode=data.opening_balance_mode,
            manual_opening_balance=manual,
            minimum_cash_buffer_type=data.minimum_cash_buffer_type,
            minimum_cash_buffer_value=data.minimum_cash_buffer_value,
        )
        # Cash plans have no separate activate endpoint; usable on create.
        plan.activate()
        saved = self._cash_plans.add(plan)
        if data.account_ids:
            self._cash_plans.replace_account_ids(
                data.organization_id,
                saved.id,
                list(data.account_ids),
            )
        return saved
