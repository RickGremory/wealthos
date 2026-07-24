"""SafeToSpendService acceptance cases."""

from decimal import Decimal

from wealthos.modules.planning.application.services.safe_to_spend_service import (
    SafeToSpendService,
)


def test_safe_to_spend_happy_path() -> None:
    result = SafeToSpendService().calculate(
        liquid_balance=Decimal("100000.00"),
        committed_outflows=Decimal("45000.00"),
        tax_reserve_shortfall=Decimal("15000.00"),
        minimum_cash_buffer=Decimal("20000.00"),
    )
    assert result.safe_to_spend == Decimal("20000.00")
    assert result.funding_gap == Decimal("0.00")


def test_safe_to_spend_floors_at_zero_and_reports_gap() -> None:
    result = SafeToSpendService().calculate(
        liquid_balance=Decimal("50000.00"),
        committed_outflows=Decimal("45000.00"),
        tax_reserve_shortfall=Decimal("15000.00"),
        minimum_cash_buffer=Decimal("20000.00"),
    )
    assert result.safe_to_spend == Decimal("0.00")
    assert result.funding_gap == Decimal("30000.00")
