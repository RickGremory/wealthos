"""GetTaxProfile query."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.taxes.domain.entities.tax_profile import TaxProfile
from wealthos.modules.taxes.domain.exceptions import TaxProfileNotFound
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)


class GetTaxProfileQuery:
    def __init__(self, profiles: TaxProfileRepository) -> None:
        self._profiles = profiles

    def execute(self, organization_id: UUID, profile_id: UUID) -> TaxProfile:
        profile = self._profiles.get_by_id(organization_id, profile_id)
        if profile is None:
            raise TaxProfileNotFound("Tax profile not found.")
        return profile
