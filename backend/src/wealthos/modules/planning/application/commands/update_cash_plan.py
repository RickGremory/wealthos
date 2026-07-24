"""UpdateCashPlan command."""

from __future__ import annotations

from dataclasses import dataclass, field
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
from wealthos.modules.planning.domain.exceptions import (
    CashPlanNotFoundError,
    SelectedAccountsRequired,
)
from wealthos.modules.planning.domain.repositories.cash_plan_repository import (
    CashPlanRepository,
)
from wealthos.modules.planning.domain.value_objects.opening_balance_mode import (
    OpeningBalanceMode,
)
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class UpdateCashPlanInput:
    organization_id: UUID
    cash_plan_id: UUID
    name: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    opening_balance_mode: str | None = None
    manual_opening_balance: Decimal | None = None
    account_ids: tuple[UUID, ...] | None = None
    minimum_cash_buffer_type: str | None = None
    minimum_cash_buffer_value: Decimal | None = None
    fields_set: frozenset[str] = field(default_factory=frozenset)


class UpdateCashPlanCommand:
    def __init__(
        self,
        cash_plans: CashPlanRepository,
        accounts: AccountRepository,
    ) -> None:
        self._cash_plans = cash_plans
        self._validator = LinkedResourceValidator(accounts=accounts)

    def execute(self, data: UpdateCashPlanInput) -> CashPlan:
        plan = self._cash_plans.get_by_id(data.organization_id, data.cash_plan_id)
        if plan is None:
            raise CashPlanNotFoundError("Cash plan not found.")

        if "name" in data.fields_set and data.name is not None:
            plan.rename(data.name)
        if "date_from" in data.fields_set or "date_to" in data.fields_set:
            plan.change_dates(
                data.date_from if data.date_from is not None else plan.date_from,
                data.date_to if data.date_to is not None else plan.date_to,
            )

        if "opening_balance_mode" in data.fields_set or "manual_opening_balance" in data.fields_set:
            mode = (
                data.opening_balance_mode
                if data.opening_balance_mode is not None
                else plan.opening_balance_mode.value
            )
            manual = None
            if OpeningBalanceMode(mode).is_manual:
                if "manual_opening_balance" in data.fields_set:
                    if data.manual_opening_balance is None:
                        manual = None
                    else:
                        manual = Money(data.manual_opening_balance, plan.currency)
                else:
                    manual = plan.manual_opening_balance
            plan.change_opening_balance(mode, manual)

        if (
            "minimum_cash_buffer_type" in data.fields_set
            or "minimum_cash_buffer_value" in data.fields_set
        ):
            plan.change_cash_buffer(
                data.minimum_cash_buffer_type
                if data.minimum_cash_buffer_type is not None
                else plan.minimum_cash_buffer_type.value,
                data.minimum_cash_buffer_value
                if data.minimum_cash_buffer_value is not None
                else plan.minimum_cash_buffer_value,
            )

        saved = self._cash_plans.save(plan)

        if "account_ids" in data.fields_set:
            account_ids = data.account_ids or ()
            if saved.opening_balance_mode.is_selected_accounts and not account_ids:
                raise SelectedAccountsRequired(
                    "selected_accounts opening balance mode requires account_ids."
                )
            currency = saved.currency.value
            for account_id in account_ids:
                self._validator.ensure_account(data.organization_id, account_id, currency)
            self._cash_plans.replace_account_ids(
                data.organization_id,
                data.cash_plan_id,
                list(account_ids),
            )
        return saved
