"""Tax domain entity tests."""

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from wealthos.modules.taxes.domain.entities.tax_payment import TaxPayment
from wealthos.modules.taxes.domain.entities.tax_period import TaxPeriod
from wealthos.modules.taxes.domain.entities.tax_profile import TaxProfile
from wealthos.modules.taxes.domain.entities.tax_rule import TaxRule
from wealthos.modules.taxes.domain.exceptions import (
    InvalidFiscalYearStartMonth,
    InvalidTaxPeriod,
    InvalidTaxRule,
    TaxPaymentAmountInvalid,
    TaxPeriodAlreadyClosed,
    TaxPeriodClosed,
    TaxPeriodNotCalculated,
    TaxRuleAlreadyArchived,
)
from wealthos.shared.domain.value_objects.money import Money


def test_create_tax_profile() -> None:
    profile = TaxProfile.create(
        organization_id=uuid4(),
        country_code="MX",
        taxpayer_type="individual",
        filing_frequency="monthly",
        currency="MXN",
    )
    assert profile.is_active
    assert profile.country_code.value == "MX"


def test_invalid_fiscal_year_start_month() -> None:
    with pytest.raises(InvalidFiscalYearStartMonth):
        TaxProfile.create(
            organization_id=uuid4(),
            country_code="MX",
            taxpayer_type="individual",
            filing_frequency="monthly",
            currency="MXN",
            fiscal_year_start_month=13,
        )


def test_tax_profile_update_and_deactivate() -> None:
    profile = TaxProfile.create(
        organization_id=uuid4(),
        country_code="MX",
        taxpayer_type="individual",
        filing_frequency="monthly",
        currency="MXN",
    )
    profile.update(jurisdiction="CDMX", fields_set=frozenset({"jurisdiction"}))
    assert profile.jurisdiction == "CDMX"
    profile.deactivate()
    assert profile.is_active is False


def test_create_percentage_tax_rule() -> None:
    rule = TaxRule.create(
        organization_id=uuid4(),
        tax_profile_id=uuid4(),
        name="ISR estimado",
        tax_type="income_tax",
        calculation_method="percentage",
        applies_to="net_income",
        effective_from=date(2026, 1, 1),
        rate=Decimal("15"),
    )
    assert rule.rate is not None
    assert rule.rate.value == Decimal("15.0000")


def test_percentage_rule_requires_rate() -> None:
    with pytest.raises(InvalidTaxRule):
        TaxRule.create(
            organization_id=uuid4(),
            tax_profile_id=uuid4(),
            name="Bad",
            tax_type="income_tax",
            calculation_method="percentage",
            applies_to="net_income",
            effective_from=date(2026, 1, 1),
        )


def test_archive_tax_rule() -> None:
    rule = TaxRule.create(
        organization_id=uuid4(),
        tax_profile_id=uuid4(),
        name="ISR",
        tax_type="income_tax",
        calculation_method="percentage",
        applies_to="net_income",
        effective_from=date(2026, 1, 1),
        rate=Decimal("15"),
    )
    rule.archive()
    assert rule.archived_at is not None
    with pytest.raises(TaxRuleAlreadyArchived):
        rule.archive()


def test_tax_period_lifecycle() -> None:
    period = TaxPeriod.create(
        organization_id=uuid4(),
        tax_profile_id=uuid4(),
        period_type="monthly",
        date_from=date(2026, 7, 1),
        date_to=date(2026, 7, 31),
        currency="MXN",
    )
    assert period.status.value == "open"
    period.mark_calculated()
    assert period.status.value == "calculated"
    period.close()
    assert period.status.value == "closed"
    with pytest.raises(TaxPeriodAlreadyClosed):
        period.close()


def test_cannot_calculate_closed_period() -> None:
    period = TaxPeriod.create(
        organization_id=uuid4(),
        tax_profile_id=uuid4(),
        period_type="monthly",
        date_from=date(2026, 7, 1),
        date_to=date(2026, 7, 31),
        currency="MXN",
    )
    period.mark_calculated()
    period.close()
    with pytest.raises(TaxPeriodClosed):
        period.ensure_can_calculate()


def test_close_requires_calculated() -> None:
    period = TaxPeriod.create(
        organization_id=uuid4(),
        tax_profile_id=uuid4(),
        period_type="monthly",
        date_from=date(2026, 7, 1),
        date_to=date(2026, 7, 31),
        currency="MXN",
    )
    with pytest.raises(TaxPeriodNotCalculated):
        period.close()


def test_invalid_period_range() -> None:
    with pytest.raises(InvalidTaxPeriod):
        TaxPeriod.create(
            organization_id=uuid4(),
            tax_profile_id=uuid4(),
            period_type="monthly",
            date_from=date(2026, 7, 31),
            date_to=date(2026, 7, 1),
            currency="MXN",
        )


def test_tax_payment_positive_amount() -> None:
    payment = TaxPayment.create(
        organization_id=uuid4(),
        tax_period_id=uuid4(),
        tax_type="income_tax",
        transaction_id=uuid4(),
        source_account_id=uuid4(),
        amount=Money(Decimal("100.00"), "MXN"),
        paid_at=datetime.now(UTC),
        created_by_user_id=uuid4(),
    )
    assert payment.amount.amount == Decimal("100.00")


def test_tax_payment_rejects_non_positive() -> None:
    with pytest.raises(TaxPaymentAmountInvalid):
        TaxPayment.create(
            organization_id=uuid4(),
            tax_period_id=uuid4(),
            tax_type="income_tax",
            transaction_id=uuid4(),
            source_account_id=uuid4(),
            amount=Money(Decimal("0.00"), "MXN"),
            paid_at=datetime.now(UTC),
            created_by_user_id=uuid4(),
        )
