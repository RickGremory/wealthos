"""Mexico tax calculation service acceptance test."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

from wealthos.modules.tax_mx.application.services.mexico_tax_calculation_service import (
    ClassificationBundle,
    MexicoTaxCalculationService,
    MexicoTaxTransactionView,
)
from wealthos.modules.tax_mx.domain.entities.mexico_tax_classification import (
    MexicoTaxCategoryMapping,
)
from wealthos.modules.tax_mx.domain.entities.mexico_tax_configuration import (
    MexicoTaxConfiguration,
)
from wealthos.modules.tax_mx.domain.entities.tax_evidence import MexicoTransactionTaxDetails
from wealthos.shared.domain.value_objects.money import Money


def test_mexico_monthly_acceptance_case() -> None:
    org_id = uuid4()
    profile_id = uuid4()
    income_cat = uuid4()
    expense_cat = uuid4()
    income_tx = uuid4()
    expense_tx = uuid4()

    configuration = MexicoTaxConfiguration.create(
        organization_id=org_id,
        tax_profile_id=profile_id,
        version=1,
        rfc="XAXX010101000",
        person_type="individual",
        tax_regime_code="626",
        vat_enabled=True,
        income_tax_enabled=True,
        effective_from=date(2026, 1, 1),
        default_vat_rate=Decimal("16"),
        income_tax_estimation_method="configured_rate",
        income_tax_estimation_base="gross_taxable_income",
        income_tax_estimation_rate=Decimal("10"),
        requires_invoice_evidence=False,
    )

    income = MexicoTaxTransactionView(
        transaction_id=income_tx,
        transaction_type="income",
        status="posted",
        occurred_on=date(2026, 7, 10),
        amount=Decimal("116000.00"),
        currency="MXN",
        category_id=income_cat,
        description="Ingreso servicios",
        amount_includes_vat=True,
    )
    expense = MexicoTaxTransactionView(
        transaction_id=expense_tx,
        transaction_type="expense",
        status="posted",
        occurred_on=date(2026, 7, 12),
        amount=Decimal("34800.00"),
        currency="MXN",
        category_id=expense_cat,
        description="Gasto operativo",
        amount_includes_vat=True,
    )

    mappings = {
        income_cat: MexicoTaxCategoryMapping.create(
            organization_id=org_id,
            tax_profile_id=profile_id,
            category_id=income_cat,
            vat_treatment="taxable",
            income_treatment="taxable",
        ),
        expense_cat: MexicoTaxCategoryMapping.create(
            organization_id=org_id,
            tax_profile_id=profile_id,
            category_id=expense_cat,
            vat_treatment="taxable",
            expense_treatment="deductible",
        ),
    }
    details = {
        income_tx: MexicoTransactionTaxDetails.create(
            organization_id=org_id,
            transaction_id=income_tx,
            subtotal=Money(Decimal("100000"), "MXN"),
            vat_amount=Money(Decimal("16000"), "MXN"),
            total=Money(Decimal("116000"), "MXN"),
        )
    }
    bundle = ClassificationBundle(
        mappings=mappings,
        overrides={},
        details=details,
        evidence_status_by_tx={},
        withholdings_income_tax={income_tx: Decimal("1000")},
        withholdings_vat={},
    )

    workpaper = MexicoTaxCalculationService().calculate(
        period_id=uuid4(),
        configuration=configuration,
        transactions=[income, expense],
        bundle=bundle,
        currency="MXN",
    )

    assert workpaper.taxable_income == Decimal("100000.00")
    assert workpaper.output_vat == Decimal("16000.00")
    assert workpaper.deductible_expenses == Decimal("30000.00")
    assert workpaper.creditable_vat == Decimal("4800.00")
    assert workpaper.estimated_income_tax == Decimal("10000.00")
    assert workpaper.withheld_income_tax == Decimal("1000.00")
    assert workpaper.income_tax_due == Decimal("9000.00")
    assert workpaper.vat_due == Decimal("11200.00")
    assert workpaper.estimated_total_due == Decimal("20200.00")
