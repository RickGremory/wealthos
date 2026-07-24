"""UpdateMexicoTaxCategoryMapping command."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from wealthos.modules.tax_mx.domain.exceptions import MexicoClassificationNotFound
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_category_mapping_repository import (
    MexicoTaxCategoryMappingRepository,
)


@dataclass(frozen=True, slots=True)
class UpdateMexicoTaxCategoryMappingInput:
    organization_id: UUID
    mapping_id: UUID
    vat_treatment: str | None = None
    income_treatment: str | None = None
    expense_treatment: str | None = None
    deductibility_percentage: Decimal | None = None
    vat_creditable_percentage: Decimal | None = None
    requires_cfdi: bool | None = None
    requires_payment_evidence: bool | None = None
    clear_income_treatment: bool = False
    clear_expense_treatment: bool = False
    fields_set: frozenset[str] = frozenset()


class UpdateMexicoTaxCategoryMappingCommand:
    def __init__(self, mappings: MexicoTaxCategoryMappingRepository) -> None:
        self._mappings = mappings

    def execute(self, data: UpdateMexicoTaxCategoryMappingInput):
        mapping = self._mappings.get_by_id(data.organization_id, data.mapping_id)
        if mapping is None:
            raise MexicoClassificationNotFound("Category mapping not found.")
        mapping.update(
            vat_treatment=data.vat_treatment,
            income_treatment=data.income_treatment,
            expense_treatment=data.expense_treatment,
            deductibility_percentage=data.deductibility_percentage,
            vat_creditable_percentage=data.vat_creditable_percentage,
            requires_cfdi=data.requires_cfdi,
            requires_payment_evidence=data.requires_payment_evidence,
            clear_income_treatment=data.clear_income_treatment,
            clear_expense_treatment=data.clear_expense_treatment,
            fields_set=data.fields_set,
        )
        return self._mappings.save(mapping)
