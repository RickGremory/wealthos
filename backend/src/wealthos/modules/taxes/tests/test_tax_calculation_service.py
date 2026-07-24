"""TaxCalculationService verified scenario tests."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

from wealthos.modules.taxes.application.services.tax_calculation_service import (
    ClassificationContext,
    TaxCalculationService,
    TaxTransactionView,
)
from wealthos.modules.taxes.domain.entities.tax_profile import TaxProfile
from wealthos.modules.taxes.domain.entities.tax_rule import TaxRule


def test_verified_calculation_case() -> None:
    org_id = uuid4()
    period_id = uuid4()
    user_id = uuid4()
    income_cat = uuid4()
    expense_cat = uuid4()

    profile = TaxProfile.create(
        organization_id=org_id,
        country_code="MX",
        taxpayer_type="individual",
        filing_frequency="monthly",
        currency="MXN",
    )
    rule = TaxRule.create(
        organization_id=org_id,
        tax_profile_id=profile.id,
        name="ISR 15%",
        tax_type="income_tax",
        calculation_method="percentage",
        applies_to="net_income",
        effective_from=date(2026, 1, 1),
        rate=Decimal("15"),
    )

    non_taxable_cat = uuid4()
    context = ClassificationContext(
        category_mappings={
            income_cat: ("taxable_income", Decimal("100")),
            non_taxable_cat: ("non_taxable_income", Decimal("100")),
            expense_cat: ("deductible_expense", Decimal("100")),
        },
        transaction_overrides={},
    )
    transactions = [
        TaxTransactionView(
            transaction_id=uuid4(),
            transaction_type="income",
            status="posted",
            occurred_on=date(2026, 7, 5),
            amount=Decimal("50000.00"),
            currency="MXN",
            category_id=income_cat,
        ),
        TaxTransactionView(
            transaction_id=uuid4(),
            transaction_type="income",
            status="posted",
            occurred_on=date(2026, 7, 6),
            amount=Decimal("5000.00"),
            currency="MXN",
            category_id=non_taxable_cat,
        ),
        TaxTransactionView(
            transaction_id=uuid4(),
            transaction_type="expense",
            status="posted",
            occurred_on=date(2026, 7, 7),
            amount=Decimal("-12000.00"),
            currency="MXN",
            category_id=expense_cat,
        ),
    ]

    calculation, paid = TaxCalculationService().calculate(
        profile=profile,
        period_id=period_id,
        period_from=date(2026, 7, 1),
        period_to=date(2026, 7, 31),
        rules=[rule],
        transactions=transactions,
        payments=[],
        context=context,
        version=1,
        performed_by_user_id=user_id,
    )

    assert calculation.gross_income.amount == Decimal("55000.00")
    assert calculation.taxable_income.amount == Decimal("50000.00")
    assert calculation.deductible_expenses.amount == Decimal("12000.00")
    assert calculation.taxable_base.amount == Decimal("38000.00")
    assert calculation.estimated_tax.amount == Decimal("5700.00")
    assert paid == Decimal("0.00")
