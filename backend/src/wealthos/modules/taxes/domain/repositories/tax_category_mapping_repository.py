"""Persistence port for TaxCategoryMapping."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.taxes.domain.entities.tax_category_mapping import TaxCategoryMapping


class TaxCategoryMappingRepository(Protocol):
    def upsert(self, mapping: TaxCategoryMapping) -> TaxCategoryMapping: ...

    def list_by_profile(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
    ) -> list[TaxCategoryMapping]: ...

    def get_by_category(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
        category_id: UUID,
    ) -> TaxCategoryMapping | None: ...
