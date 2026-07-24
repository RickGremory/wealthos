"""Mexico tax domain entity tests."""

from datetime import date
from decimal import Decimal

import pytest

from wealthos.modules.tax_mx.domain.entities.mexico_tax_classification import (
    MexicoTaxCategoryMapping,
)
from wealthos.modules.tax_mx.domain.entities.mexico_tax_configuration import (
    MexicoTaxConfiguration,
)
from wealthos.modules.tax_mx.domain.entities.tax_evidence import MexicoTransactionTaxDetails
from wealthos.modules.tax_mx.domain.exceptions import (
    CashFlowBasisRequired,
    InvalidMexicoTaxConfiguration,
    InvalidTaxDetails,
)
from wealthos.shared.domain.value_objects.money import Money


def test_mexico_tax_configuration_requires_cash_basis() -> None:
    with pytest.raises(CashFlowBasisRequired):
        MexicoTaxConfiguration.create(
            organization_id=__import__("uuid").uuid4(),
            tax_profile_id=__import__("uuid").uuid4(),
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
            cash_flow_basis=False,
        )


def test_mexico_tax_configuration_requires_vat_rate_when_enabled() -> None:
    with pytest.raises(InvalidMexicoTaxConfiguration):
        MexicoTaxConfiguration.create(
            organization_id=__import__("uuid").uuid4(),
            tax_profile_id=__import__("uuid").uuid4(),
            version=1,
            rfc="XAXX010101000",
            person_type="individual",
            tax_regime_code="626",
            vat_enabled=True,
            income_tax_enabled=False,
            effective_from=date(2026, 1, 1),
            default_vat_rate=None,
        )


def test_category_mapping_create() -> None:
    mapping = MexicoTaxCategoryMapping.create(
        organization_id=__import__("uuid").uuid4(),
        tax_profile_id=__import__("uuid").uuid4(),
        category_id=__import__("uuid").uuid4(),
        vat_treatment="taxable",
        income_treatment="taxable",
    )
    assert mapping.vat_treatment.value == "taxable"


def test_tax_details_reconcile_total() -> None:
    with pytest.raises(InvalidTaxDetails):
        MexicoTransactionTaxDetails.create(
            organization_id=__import__("uuid").uuid4(),
            transaction_id=__import__("uuid").uuid4(),
            subtotal=Money(Decimal("100"), "MXN"),
            vat_amount=Money(Decimal("16"), "MXN"),
            total=Money(Decimal("200"), "MXN"),
        )
