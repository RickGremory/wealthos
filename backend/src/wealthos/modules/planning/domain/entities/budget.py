"""Budget aggregate — planned income/expense envelope for a period."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from wealthos.modules.planning.domain.exceptions import (
    BudgetAlreadyArchived,
    BudgetClosed,
    BudgetNotEditable,
    InvalidBudgetDateRange,
)
from wealthos.modules.planning.domain.value_objects.budget_name import BudgetName
from wealthos.modules.planning.domain.value_objects.budget_period_type import BudgetPeriodType
from wealthos.modules.planning.domain.value_objects.budget_status import BudgetStatus
from wealthos.modules.planning.domain.value_objects.forecast_method import ForecastMethod
from wealthos.modules.planning.domain.value_objects.period_dates import derive_period_dates
from wealthos.modules.planning.domain.value_objects.rollover_policy import RolloverPolicy
from wealthos.shared.domain.value_objects.currency import Currency


@dataclass(slots=True)
class Budget:
    id: UUID
    organization_id: UUID
    name: BudgetName
    period_type: BudgetPeriodType
    date_from: date
    date_to: date
    currency: Currency
    status: BudgetStatus
    rollover_policy: RolloverPolicy
    forecast_method: ForecastMethod
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None
    archived_at: datetime | None

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        name: str,
        period_type: str,
        currency: str,
        rollover_policy: str = "none",
        forecast_method: str = "linear",
        reference_date: date | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        budget_id: UUID | None = None,
    ) -> Budget:
        period = BudgetPeriodType(period_type)
        derived_from, derived_to = derive_period_dates(
            period,
            reference_date=reference_date,
            date_from=date_from,
            date_to=date_to,
        )
        now = datetime.now(UTC)
        return cls(
            id=budget_id or uuid4(),
            organization_id=organization_id,
            name=BudgetName(name),
            period_type=period,
            date_from=derived_from,
            date_to=derived_to,
            currency=Currency(currency),
            status=BudgetStatus("draft"),
            rollover_policy=RolloverPolicy(rollover_policy),
            forecast_method=ForecastMethod(forecast_method),
            created_at=now,
            updated_at=now,
            closed_at=None,
            archived_at=None,
        )

    def rename(self, name: str) -> None:
        self.ensure_mutable()
        self.name = BudgetName(name)
        self.updated_at = datetime.now(UTC)

    def change_dates(self, date_from: date, date_to: date) -> None:
        self.ensure_mutable()
        if not self.period_type.is_custom:
            raise BudgetNotEditable("Only custom budgets can change dates.")
        if date_from > date_to:
            raise InvalidBudgetDateRange("date_from must be on or before date_to.")
        self.date_from = date_from
        self.date_to = date_to
        self.updated_at = datetime.now(UTC)

    def change_rollover_policy(self, rollover_policy: str) -> None:
        self.ensure_mutable()
        self.rollover_policy = RolloverPolicy(rollover_policy)
        self.updated_at = datetime.now(UTC)

    def change_forecast_method(self, forecast_method: str) -> None:
        self.ensure_mutable()
        self.forecast_method = ForecastMethod(forecast_method)
        self.updated_at = datetime.now(UTC)

    def activate(self) -> None:
        self._ensure_not_archived()
        if self.status.is_closed:
            raise BudgetClosed("Cannot activate a closed budget.")
        if not self.status.is_draft:
            raise BudgetNotEditable("Only draft budgets can be activated.")
        now = datetime.now(UTC)
        self.status = BudgetStatus("active")
        self.updated_at = now

    def close(self) -> None:
        self._ensure_not_archived()
        if self.status.is_closed:
            raise BudgetClosed("Budget is already closed.")
        if not self.status.is_active:
            raise BudgetNotEditable("Only active budgets can be closed.")
        now = datetime.now(UTC)
        self.status = BudgetStatus("closed")
        self.closed_at = now
        self.updated_at = now

    def archive(self) -> None:
        if self.status.is_archived:
            raise BudgetAlreadyArchived("Budget is already archived.")
        now = datetime.now(UTC)
        self.status = BudgetStatus("archived")
        self.archived_at = now
        self.updated_at = now

    def ensure_allocations_editable(self) -> None:
        if self.status.is_archived:
            raise BudgetAlreadyArchived("Cannot modify allocations on an archived budget.")
        if self.status.is_closed:
            raise BudgetClosed("Cannot modify allocations on a closed budget.")

    def ensure_mutable(self) -> None:
        if self.status.is_archived:
            raise BudgetAlreadyArchived("Cannot update an archived budget.")
        if self.status.is_closed:
            raise BudgetClosed("Cannot update a closed budget.")
        if not self.status.is_editable:
            raise BudgetNotEditable("Budget is not editable in its current status.")

    def _ensure_not_archived(self) -> None:
        if self.status.is_archived:
            raise BudgetAlreadyArchived("Cannot operate on an archived budget.")
