"""CashProjectionService acceptance cases."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

from wealthos.modules.planning.application.services.cash_projection_service import (
    CashProjectionInput,
    CashProjectionItem,
    CashProjectionService,
)


def _item(
    *,
    item_type: str,
    expected_date: date,
    amount: Decimal,
    probability: Decimal = Decimal("100"),
    status: str = "planned",
    matched_amount: Decimal = Decimal("0"),
    matched_dates: tuple[date, ...] = (),
) -> CashProjectionItem:
    return CashProjectionItem(
        item_id=uuid4(),
        item_type=item_type,
        expected_date=expected_date,
        amount=amount,
        probability=probability,
        status=status,
        matched_amount=matched_amount,
        matched_dates=matched_dates,
    )


def test_temporary_shortfall_detected_even_when_ending_positive() -> None:
    """Opening 20k, tax -25k d10, rent -10k d12, inflow +30k d15 → shortfall d10."""
    service = CashProjectionService()
    projection = service.project(
        CashProjectionInput(
            opening_balance=Decimal("20000.00"),
            date_from=date(2026, 8, 1),
            date_to=date(2026, 8, 20),
            scenario="committed",
            items=(
                _item(
                    item_type="outflow",
                    expected_date=date(2026, 8, 10),
                    amount=Decimal("25000.00"),
                    status="confirmed",
                ),
                _item(
                    item_type="outflow",
                    expected_date=date(2026, 8, 12),
                    amount=Decimal("10000.00"),
                    status="confirmed",
                ),
                _item(
                    item_type="inflow",
                    expected_date=date(2026, 8, 15),
                    amount=Decimal("30000.00"),
                    status="confirmed",
                ),
            ),
        )
    )

    by_date = {p.date: p for p in projection.points}
    assert by_date[date(2026, 8, 10)].ending_balance == Decimal("-5000.00")
    assert by_date[date(2026, 8, 12)].ending_balance == Decimal("-15000.00")
    assert by_date[date(2026, 8, 15)].ending_balance == Decimal("15000.00")
    assert projection.ending_balance == Decimal("15000.00")
    assert projection.minimum_balance == Decimal("-15000.00")
    assert projection.first_shortfall_date == date(2026, 8, 10)


def test_expected_scenario_weights_inflows_keeps_full_outflows() -> None:
    service = CashProjectionService()
    projection = service.project(
        CashProjectionInput(
            opening_balance=Decimal("10000.00"),
            date_from=date(2026, 8, 1),
            date_to=date(2026, 8, 5),
            scenario="expected",
            items=(
                _item(
                    item_type="inflow",
                    expected_date=date(2026, 8, 2),
                    amount=Decimal("10000.00"),
                    probability=Decimal("60"),
                    status="planned",
                ),
                _item(
                    item_type="outflow",
                    expected_date=date(2026, 8, 3),
                    amount=Decimal("4000.00"),
                    probability=Decimal("50"),
                    status="planned",
                ),
            ),
        )
    )
    by_date = {p.date: p for p in projection.points}
    assert by_date[date(2026, 8, 2)].inflows == Decimal("6000.00")
    assert by_date[date(2026, 8, 3)].outflows == Decimal("4000.00")
    assert projection.ending_balance == Decimal("12000.00")


def test_same_day_outflows_before_inflows_intraday_min() -> None:
    service = CashProjectionService()
    projection = service.project(
        CashProjectionInput(
            opening_balance=Decimal("5000.00"),
            date_from=date(2026, 8, 1),
            date_to=date(2026, 8, 1),
            scenario="optimistic",
            items=(
                _item(
                    item_type="outflow",
                    expected_date=date(2026, 8, 1),
                    amount=Decimal("8000.00"),
                ),
                _item(
                    item_type="inflow",
                    expected_date=date(2026, 8, 1),
                    amount=Decimal("10000.00"),
                ),
            ),
        )
    )
    point = projection.points[0]
    assert point.ending_balance == Decimal("7000.00")
    assert point.lowest_intraday_balance == Decimal("-3000.00")
    assert projection.minimum_balance == Decimal("-3000.00")
    assert projection.first_shortfall_date == date(2026, 8, 1)


def test_committed_excludes_low_probability_remaining() -> None:
    service = CashProjectionService()
    projection = service.project(
        CashProjectionInput(
            opening_balance=Decimal("0.00"),
            date_from=date(2026, 8, 1),
            date_to=date(2026, 8, 5),
            scenario="committed",
            items=(
                _item(
                    item_type="inflow",
                    expected_date=date(2026, 8, 2),
                    amount=Decimal("10000.00"),
                    probability=Decimal("60"),
                    status="planned",
                ),
                _item(
                    item_type="inflow",
                    expected_date=date(2026, 8, 3),
                    amount=Decimal("5000.00"),
                    probability=Decimal("100"),
                    status="planned",
                ),
            ),
        )
    )
    by_date = {p.date: p for p in projection.points}
    assert by_date[date(2026, 8, 2)].inflows == Decimal("0.00")
    assert by_date[date(2026, 8, 3)].inflows == Decimal("5000.00")


def test_partial_match_uses_real_date_and_remaining_expected() -> None:
    service = CashProjectionService()
    projection = service.project(
        CashProjectionInput(
            opening_balance=Decimal("0.00"),
            date_from=date(2026, 8, 1),
            date_to=date(2026, 8, 15),
            scenario="optimistic",
            items=(
                _item(
                    item_type="inflow",
                    expected_date=date(2026, 8, 10),
                    amount=Decimal("50000.00"),
                    status="partially_matched",
                    matched_amount=Decimal("30000.00"),
                    matched_dates=(date(2026, 8, 9),),
                ),
            ),
        )
    )
    by_date = {p.date: p for p in projection.points}
    assert by_date[date(2026, 8, 9)].inflows == Decimal("30000.00")
    assert by_date[date(2026, 8, 10)].inflows == Decimal("20000.00")


def test_cancelled_items_are_skipped() -> None:
    service = CashProjectionService()
    projection = service.project(
        CashProjectionInput(
            opening_balance=Decimal("1000.00"),
            date_from=date(2026, 8, 1),
            date_to=date(2026, 8, 2),
            scenario="optimistic",
            items=(
                _item(
                    item_type="outflow",
                    expected_date=date(2026, 8, 1),
                    amount=Decimal("500.00"),
                    status="cancelled",
                ),
            ),
        )
    )
    assert projection.ending_balance == Decimal("1000.00")
    assert projection.first_shortfall_date is None
