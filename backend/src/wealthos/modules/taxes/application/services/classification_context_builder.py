"""Build classification context from tax mappings and overrides."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from wealthos.modules.taxes.application.services.tax_calculation_service import (
    ClassificationContext,
)
from wealthos.modules.taxes.domain.entities.tax_category_mapping import TaxCategoryMapping
from wealthos.modules.taxes.domain.entities.tax_transaction_override import (
    TaxTransactionOverride,
)


def build_classification_context(
    mappings: list[TaxCategoryMapping],
    overrides: list[TaxTransactionOverride],
) -> ClassificationContext:
    category_mappings: dict[UUID, tuple[str, Decimal]] = {
        mapping.category_id: (
            mapping.tax_treatment.value,
            mapping.deductibility_percentage.value,
        )
        for mapping in mappings
    }
    transaction_overrides: dict[UUID, tuple[str, Decimal]] = {
        override.transaction_id: (
            override.tax_treatment.value,
            override.deductibility_percentage.value,
        )
        for override in overrides
    }
    return ClassificationContext(
        category_mappings=category_mappings,
        transaction_overrides=transaction_overrides,
    )
