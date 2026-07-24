"""CashPlan aggregate — dated liquidity projection horizon."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.planning.domain.exceptions import (
    CashPlanAlreadyArchived,
    InvalidCashPlanDateRange,
    OpeningBalanceInvalid,
    PlanningError,
)
from wealthos.modules.planning.domain.value_objects.cash_buffer_type import CashBufferType
from wealthos.modules.planning.domain.value_objects.cash_plan_name import CashPlanName
from wealthos.modules.planning.domain.value_objects.cash_plan_status import CashPlanStatus
from wealthos.modules.planning.domain.value_objects.opening_balance_mode import OpeningBalanceMode
from wealthos.shared.domain.value_objects.currency import Currency
from wealthos.shared.domain.value_objects.money import Money


@dataclass(slots=True)
class CashPlan:
    id: UUID
    organization_id: UUID
    name: CashPlanName
    date_from: date
    date_to: date
    currency: Currency
    opening_balance_mode: OpeningBalanceMode
    manual_opening_balance: Money | None
    minimum_cash_buffer_type: CashBufferType
    minimum_cash_buffer_value: Decimal
    status: CashPlanStatus
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        name: str,
        date_from: date,
        date_to: date,
        currency: str,
        opening_balance_mode: str,
        manual_opening_balance: Money | None = None,
        minimum_cash_buffer_type: str = "fixed_amount",
        minimum_cash_buffer_value: Decimal | str | int = "0.00",
        cash_plan_id: UUID | None = None,
    ) -> CashPlan:
        if date_from > date_to:
            raise InvalidCashPlanDateRange("date_from must be on or before date_to.")

        mode = OpeningBalanceMode(opening_balance_mode)
        if mode.is_manual and manual_opening_balance is None:
            raise OpeningBalanceInvalid(
                "manual opening balance mode requires manual_opening_balance."
            )
        if not mode.is_manual and manual_opening_balance is not None:
            raise OpeningBalanceInvalid(
                "manual_opening_balance is only allowed for manual opening balance mode."
            )
        if manual_opening_balance is not None:
            money_currency = Currency(currency)
            if manual_opening_balance.currency != money_currency:
                raise OpeningBalanceInvalid(
                    "manual_opening_balance currency must match plan currency."
                )

        if isinstance(minimum_cash_buffer_value, float):
            raise TypeError("minimum_cash_buffer_value does not accept float.")
        buffer_value = (
            minimum_cash_buffer_value
            if isinstance(minimum_cash_buffer_value, Decimal)
            else Decimal(str(minimum_cash_buffer_value))
        )
        if buffer_value < 0:
            raise OpeningBalanceInvalid("minimum_cash_buffer_value cannot be negative.")

        now = datetime.now(UTC)
        return cls(
            id=cash_plan_id or uuid4(),
            organization_id=organization_id,
            name=CashPlanName(name),
            date_from=date_from,
            date_to=date_to,
            currency=Currency(currency),
            opening_balance_mode=mode,
            manual_opening_balance=manual_opening_balance,
            minimum_cash_buffer_type=CashBufferType(minimum_cash_buffer_type),
            minimum_cash_buffer_value=buffer_value,
            status=CashPlanStatus("draft"),
            created_at=now,
            updated_at=now,
            archived_at=None,
        )

    def rename(self, name: str) -> None:
        self.ensure_editable()
        self.name = CashPlanName(name)
        self.updated_at = datetime.now(UTC)

    def change_dates(self, date_from: date, date_to: date) -> None:
        self.ensure_editable()
        if date_from > date_to:
            raise InvalidCashPlanDateRange("date_from must be on or before date_to.")
        self.date_from = date_from
        self.date_to = date_to
        self.updated_at = datetime.now(UTC)

    def change_opening_balance(
        self,
        opening_balance_mode: str,
        manual_opening_balance: Money | None = None,
    ) -> None:
        self.ensure_editable()
        mode = OpeningBalanceMode(opening_balance_mode)
        if mode.is_manual and manual_opening_balance is None:
            raise OpeningBalanceInvalid(
                "manual opening balance mode requires manual_opening_balance."
            )
        if not mode.is_manual:
            manual_opening_balance = None
        elif (
            manual_opening_balance is not None and manual_opening_balance.currency != self.currency
        ):
            raise OpeningBalanceInvalid("manual_opening_balance currency must match plan currency.")
        self.opening_balance_mode = mode
        self.manual_opening_balance = manual_opening_balance
        self.updated_at = datetime.now(UTC)

    def change_cash_buffer(
        self,
        buffer_type: str,
        buffer_value: Decimal | str | int,
    ) -> None:
        self.ensure_editable()
        if isinstance(buffer_value, float):
            raise TypeError("minimum_cash_buffer_value does not accept float.")
        value = buffer_value if isinstance(buffer_value, Decimal) else Decimal(str(buffer_value))
        if value < 0:
            raise OpeningBalanceInvalid("minimum_cash_buffer_value cannot be negative.")
        self.minimum_cash_buffer_type = CashBufferType(buffer_type)
        self.minimum_cash_buffer_value = value
        self.updated_at = datetime.now(UTC)

    def activate(self) -> None:
        self.ensure_editable()
        if self.status.is_active:
            return
        if not self.status.is_draft:
            raise PlanningError("Only draft cash plans can be activated.")
        self.status = CashPlanStatus("active")
        self.updated_at = datetime.now(UTC)

    def complete(self) -> None:
        self.ensure_editable()
        now = datetime.now(UTC)
        self.status = CashPlanStatus("completed")
        self.updated_at = now

    def archive(self) -> None:
        if self.status.is_archived:
            raise CashPlanAlreadyArchived("Cash plan is already archived.")
        now = datetime.now(UTC)
        self.status = CashPlanStatus("archived")
        self.archived_at = now
        self.updated_at = now

    def ensure_editable(self) -> None:
        if self.status.is_archived:
            raise CashPlanAlreadyArchived("Cannot update an archived cash plan.")
        if self.status.is_completed:
            raise PlanningError("Cannot update a completed cash plan.")
