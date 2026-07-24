"""TaxTransactionClassifier tests."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

from wealthos.modules.taxes.application.services.tax_calculation_service import (
    ClassificationContext,
    TaxTransactionClassifier,
    TaxTransactionView,
)


def _tx(**overrides) -> TaxTransactionView:
    defaults = {
        "transaction_id": uuid4(),
        "transaction_type": "income",
        "status": "posted",
        "occurred_on": date(2026, 7, 10),
        "amount": Decimal("1000.00"),
        "currency": "MXN",
        "category_id": None,
        "linked_tax_payment": False,
    }
    defaults.update(overrides)
    return TaxTransactionView(**defaults)


def test_default_income_is_taxable() -> None:
    classifier = TaxTransactionClassifier()
    result = classifier.classify(_tx(), ClassificationContext({}, {}))
    assert result is not None
    assert result.treatment == "taxable_income"
    assert result.amount == Decimal("1000.00")


def test_transfer_like_types_are_ignored_by_caller() -> None:
    classifier = TaxTransactionClassifier()
    result = classifier.classify(
        _tx(transaction_type="transfer"),
        ClassificationContext({}, {}),
    )
    assert result is None


def test_category_mapping_overrides_default() -> None:
    category_id = uuid4()
    context = ClassificationContext(
        category_mappings={category_id: ("non_taxable_income", Decimal("100"))},
        transaction_overrides={},
    )
    result = TaxTransactionClassifier().classify(
        _tx(category_id=category_id),
        context,
    )
    assert result is not None
    assert result.treatment == "non_taxable_income"


def test_transaction_override_wins_over_category() -> None:
    tx_id = uuid4()
    category_id = uuid4()
    context = ClassificationContext(
        category_mappings={category_id: ("taxable_income", Decimal("100"))},
        transaction_overrides={tx_id: ("ignored", Decimal("100"))},
    )
    result = TaxTransactionClassifier().classify(
        _tx(transaction_id=tx_id, category_id=category_id),
        context,
    )
    assert result is not None
    assert result.treatment == "ignored"


def test_linked_tax_payment_is_ignored() -> None:
    result = TaxTransactionClassifier().classify(
        _tx(linked_tax_payment=True),
        ClassificationContext({}, {}),
    )
    assert result is not None
    assert result.treatment == "ignored"
