"""MapTaxCategory command."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from wealthos.modules.categories.domain.repositories.category_repository import (
    CategoryRepository,
)
from wealthos.modules.taxes.domain.entities.tax_category_mapping import TaxCategoryMapping
from wealthos.modules.taxes.domain.exceptions import TaxCategoryNotFound, TaxProfileNotFound
from wealthos.modules.taxes.domain.repositories.tax_category_mapping_repository import (
    TaxCategoryMappingRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)


@dataclass(frozen=True, slots=True)
class MapTaxCategoryInput:
    organization_id: UUID
    tax_profile_id: UUID
    category_id: UUID
    tax_treatment: str
    deductibility_percentage: Decimal = Decimal("100")


class MapTaxCategoryCommand:
    def __init__(
        self,
        profiles: TaxProfileRepository,
        categories: CategoryRepository,
        mappings: TaxCategoryMappingRepository,
    ) -> None:
        self._profiles = profiles
        self._categories = categories
        self._mappings = mappings

    def execute(self, data: MapTaxCategoryInput) -> TaxCategoryMapping:
        profile = self._profiles.get_by_id(data.organization_id, data.tax_profile_id)
        if profile is None:
            raise TaxProfileNotFound("Tax profile not found.")

        category = self._categories.get_by_id(data.organization_id, data.category_id)
        if category is None:
            raise TaxCategoryNotFound("Category not found.")

        mapping = TaxCategoryMapping.create(
            organization_id=data.organization_id,
            tax_profile_id=data.tax_profile_id,
            category_id=data.category_id,
            tax_treatment=data.tax_treatment,
            deductibility_percentage=data.deductibility_percentage,
        )
        return self._mappings.upsert(mapping)
