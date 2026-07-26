"""Commitment calendar projection tests."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

from wealthos.modules.debts.application.queries.get_commitment_calendar import (
    GetCommitmentCalendarQuery,
)
from wealthos.modules.debts.domain.entities.debt import Debt
from wealthos.shared.domain.value_objects.money import Money


class _DebtRepo:
    def __init__(self, debts: list[Debt]) -> None:
        self._debts = debts

    def list_by_organization(self, organization_id, **kwargs):  # noqa: ANN001
        return list(self._debts)

    def get_by_id(self, organization_id, debt_id):  # noqa: ANN001
        return next((d for d in self._debts if d.id == debt_id), None)


class _Account:
    def __init__(self, amount: Decimal) -> None:
        self.current_balance = Money(amount, "MXN")


class _AccountRepo:
    def __init__(self, balances: dict) -> None:
        self._balances = balances

    def get_by_id(self, organization_id, account_id):  # noqa: ANN001
        amount = self._balances.get(account_id)
        return _Account(amount) if amount is not None else None


def test_calendar_emits_payment_due_in_range() -> None:
    account_id = uuid4()
    debt = Debt.create(
        organization_id=uuid4(),
        account_id=account_id,
        name="HSBC",
        debt_type="credit_card",
        currency="MXN",
        due_day=20,
        minimum_payment=Money("1000.00", "MXN"),
        interest_rate="40",
    )
    query = GetCommitmentCalendarQuery(
        _DebtRepo([debt]),
        _AccountRepo({account_id: Decimal("-5000.00")}),
    )
    result = query.execute(
        debt.organization_id,
        date_from=date(2026, 7, 1),
        date_to=date(2026, 8, 31),
        today=date(2026, 7, 10),
    )
    payment_events = [e for e in result.items if e.event_type == "payment_due"]
    assert payment_events
    assert all(e.commitment_id == debt.id for e in payment_events)
