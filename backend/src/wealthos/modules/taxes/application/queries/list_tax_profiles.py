"""ListTaxProfiles query."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.taxes.domain.entities.tax_profile import TaxProfile
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)


class ListTaxProfilesQuery:
    def __init__(self, profiles: TaxProfileRepository) -> None:
        self._profiles = profiles

    def execute(self, organization_id: UUID) -> list[TaxProfile]:
        return self._profiles.list_by_organization(organization_id)
