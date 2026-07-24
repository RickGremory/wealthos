"""Persistence port for Mexico category mappings."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.tax_mx.domain.entities.mexico_tax_classification import (
    MexicoTaxCategoryMapping,
)


class MexicoTaxCategoryMappingRepository(Protocol):
    def add(self, mapping: MexicoTaxCategoryMapping) -> MexicoTaxCategoryMapping: ...

    def get_by_id(
        self, organization_id: UUID, mapping_id: UUID
    ) -> MexicoTaxCategoryMapping | None: ...

    def list_by_profile(
        self, organization_id: UUID, tax_profile_id: UUID
    ) -> list[MexicoTaxCategoryMapping]: ...

    def save(self, mapping: MexicoTaxCategoryMapping) -> MexicoTaxCategoryMapping: ...

    def get_by_category(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
        category_id: UUID,
    ) -> MexicoTaxCategoryMapping | None: ...

    def upsert(self, mapping: MexicoTaxCategoryMapping) -> MexicoTaxCategoryMapping: ...
