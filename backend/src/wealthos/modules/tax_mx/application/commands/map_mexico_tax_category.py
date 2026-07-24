"""Map and update Mexico tax category mappings."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from wealthos.modules.categories.domain.repositories.category_repository import (
    CategoryRepository,
)
from wealthos.modules.tax_mx.domain.entities.mexico_tax_classification import (
    MexicoTaxCategoryMapping,
)
from wealthos.modules.tax_mx.domain.exceptions import (
    MexicoCategoryNotFound,
    MexicoClassificationNotFound,
    MexicoTaxProfileRequired,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_category_mapping_repository import (
    MexicoTaxCategoryMappingRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)


@dataclass(frozen=True, slots=True)
class MapMexicoTaxCategoryInput:
    organization_id: UUID
    tax_profile_id: UUID
    category_id: UUID
    vat_treatment: str
    income_treatment: str | None = None
    expense_treatment: str | None = None
    deductibility_percentage: Decimal = Decimal("100")
    vat_creditable_percentage: Decimal = Decimal("100")
    requires_cfdi: bool = False
    requires_payment_evidence: bool = False


class MapMexicoTaxCategoryCommand:
    def __init__(
        self,
        mappings: MexicoTaxCategoryMappingRepository,
        profiles: TaxProfileRepository,
        categories: CategoryRepository,
    ) -> None:
        self._mappings = mappings
        self._profiles = profiles
        self._categories = categories

    def execute(self, data: MapMexicoTaxCategoryInput) -> MexicoTaxCategoryMapping:
        profile = self._profiles.get_by_id(data.organization_id, data.tax_profile_id)
        if profile is None:
            raise MexicoTaxProfileRequired("Tax profile not found.")
        category = self._categories.get_by_id(data.organization_id, data.category_id)
        if category is None:
            raise MexicoCategoryNotFound("Category not found.")
        mapping = MexicoTaxCategoryMapping.create(
            organization_id=data.organization_id,
            tax_profile_id=data.tax_profile_id,
            category_id=data.category_id,
            vat_treatment=data.vat_treatment,
            income_treatment=data.income_treatment,
            expense_treatment=data.expense_treatment,
            deductibility_percentage=data.deductibility_percentage,
            vat_creditable_percentage=data.vat_creditable_percentage,
            requires_cfdi=data.requires_cfdi,
            requires_payment_evidence=data.requires_payment_evidence,
        )
        return self._mappings.upsert(mapping)


@dataclass(frozen=True, slots=True)
class UpdateMexicoTaxCategoryMappingInput:
    organization_id: UUID
    mapping_id: UUID
    fields_set: frozenset[str]
    vat_treatment: str | None = None
    income_treatment: str | None = None
    expense_treatment: str | None = None
    deductibility_percentage: Decimal | None = None
    vat_creditable_percentage: Decimal | None = None
    requires_cfdi: bool | None = None
    requires_payment_evidence: bool | None = None
    clear_income_treatment: bool = False
    clear_expense_treatment: bool = False


class UpdateMexicoTaxCategoryMappingCommand:
    def __init__(self, mappings: MexicoTaxCategoryMappingRepository) -> None:
        self._mappings = mappings

    def execute(self, data: UpdateMexicoTaxCategoryMappingInput) -> MexicoTaxCategoryMapping:
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
