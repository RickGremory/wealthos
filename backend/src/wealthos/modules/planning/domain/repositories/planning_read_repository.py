"""Read-only planning queries over accounts, transactions, and linked modules."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from wealthos.modules.planning.domain.views import (
    BudgetActualsView,
    LiquidAccountBalanceView,
    PlanningCommitmentView,
)
from wealthos.shared.domain.value_objects.currency import Currency


class PlanningReadRepository(Protocol):
    def get_budget_actuals(
        self,
        organization_id: UUID,
        budget_id: UUID,
        *,
        date_from: date,
        date_to: date,
        currency: Currency | str,
    ) -> BudgetActualsView: ...

    def get_liquid_account_balances(
        self,
        organization_id: UUID,
        currency: Currency | str,
        account_ids: Sequence[UUID] | None = None,
    ) -> list[LiquidAccountBalanceView]: ...

    def get_average_daily_expenses(
        self,
        organization_id: UUID,
        currency: Currency | str,
        lookback_days: int,
    ) -> Decimal: ...

    def get_linked_commitments(
        self,
        organization_id: UUID,
        *,
        date_from: date,
        date_to: date,
        currency: Currency | str,
    ) -> list[PlanningCommitmentView]: ...

    def get_debt_payment_actuals(
        self,
        organization_id: UUID,
        debt_id: UUID,
        *,
        date_from: date,
        date_to: date,
    ) -> Decimal: ...

    def get_tax_payment_actuals(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
        *,
        date_from: date,
        date_to: date,
    ) -> Decimal: ...

    def get_category_type(
        self,
        organization_id: UUID,
        category_id: UUID,
    ) -> str | None: ...
