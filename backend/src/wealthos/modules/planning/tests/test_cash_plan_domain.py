"""CashPlan and CashPlanItem domain tests (sprint §53)."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from wealthos.modules.planning.domain.entities.cash_plan import CashPlan
from wealthos.modules.planning.domain.entities.cash_plan_item import CashPlanItem
from wealthos.modules.planning.domain.exceptions import (
    CashPlanAlreadyArchived,
    CashPlanItemNotMatchable,
    InvalidCashPlanDateRange,
    InvalidCashPlanItemAmount,
    InvalidProbability,
    OpeningBalanceInvalid,
)
from wealthos.shared.domain.value_objects.money import Money


def _make_plan(**overrides) -> CashPlan:
    defaults = {
        "organization_id": uuid4(),
        "name": "Agosto liquidez",
        "date_from": date(2026, 8, 1),
        "date_to": date(2026, 8, 31),
        "currency": "MXN",
        "opening_balance_mode": "manual",
        "manual_opening_balance": Money(Decimal("20000.00"), "MXN"),
    }
    defaults.update(overrides)
    return CashPlan.create(**defaults)


def _make_item(**overrides) -> CashPlanItem:
    defaults = {
        "organization_id": uuid4(),
        "cash_plan_id": uuid4(),
        "item_type": "inflow",
        "description": "Cobro cliente",
        "expected_date": date(2026, 8, 15),
        "amount": Money(Decimal("30000.00"), "MXN"),
    }
    defaults.update(overrides)
    return CashPlanItem.create(**defaults)


def test_create_manual_opening_balance() -> None:
    plan = _make_plan()
    assert plan.status.is_draft
    assert plan.opening_balance_mode.is_manual
    assert plan.manual_opening_balance is not None
    assert plan.manual_opening_balance.amount == Decimal("20000.00")


def test_create_current_liquid_rejects_manual_balance() -> None:
    with pytest.raises(OpeningBalanceInvalid):
        CashPlan.create(
            organization_id=uuid4(),
            name="Liquid",
            date_from=date(2026, 8, 1),
            date_to=date(2026, 8, 31),
            currency="MXN",
            opening_balance_mode="current_liquid_balance",
            manual_opening_balance=Money(Decimal("1000.00"), "MXN"),
        )


def test_create_manual_requires_balance() -> None:
    with pytest.raises(OpeningBalanceInvalid):
        CashPlan.create(
            organization_id=uuid4(),
            name="Manual",
            date_from=date(2026, 8, 1),
            date_to=date(2026, 8, 31),
            currency="MXN",
            opening_balance_mode="manual",
        )


def test_create_selected_accounts_mode_without_manual() -> None:
    plan = CashPlan.create(
        organization_id=uuid4(),
        name="Selected",
        date_from=date(2026, 8, 1),
        date_to=date(2026, 8, 31),
        currency="MXN",
        opening_balance_mode="selected_accounts",
    )
    assert plan.opening_balance_mode.is_selected_accounts
    assert plan.manual_opening_balance is None


def test_rejects_inverted_date_range() -> None:
    with pytest.raises(InvalidCashPlanDateRange):
        _make_plan(date_from=date(2026, 8, 31), date_to=date(2026, 8, 1))


def test_activate_and_archive() -> None:
    plan = _make_plan()
    plan.activate()
    assert plan.status.is_active
    plan.archive()
    assert plan.status.is_archived
    assert plan.archived_at is not None
    with pytest.raises(CashPlanAlreadyArchived):
        plan.archive()
    with pytest.raises(CashPlanAlreadyArchived):
        plan.ensure_editable()


def test_item_requires_positive_amount() -> None:
    with pytest.raises(InvalidCashPlanItemAmount):
        _make_item(amount=Money(Decimal("0.00"), "MXN"))


def test_item_rejects_invalid_probability() -> None:
    with pytest.raises(InvalidProbability):
        _make_item(probability=Decimal("150"))
    with pytest.raises(InvalidProbability):
        _make_item(probability=Decimal("-1"))


def test_item_cancel_and_match_helpers() -> None:
    item = _make_item()
    assert item.status.is_matchable
    item.mark_partially_matched()
    assert item.status.is_partially_matched
    item.mark_matched()
    assert item.status.is_matched
    with pytest.raises(CashPlanItemNotMatchable):
        item.cancel()


def test_cancel_planned_item() -> None:
    item = _make_item()
    item.cancel()
    assert item.status.is_cancelled
    assert item.cancelled_at is not None
    with pytest.raises(CashPlanItemNotMatchable):
        item.ensure_matchable()
