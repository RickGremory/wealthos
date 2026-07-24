"""GetMexicoTaxConfiguration query."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.tax_mx.domain.exceptions import MexicoTaxConfigurationNotFound
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_configuration_repository import (
    MexicoTaxConfigurationRepository,
)


class GetMexicoTaxConfigurationQuery:
    def __init__(self, configurations: MexicoTaxConfigurationRepository) -> None:
        self._configurations = configurations

    def execute(self, organization_id: UUID, tax_profile_id: UUID):
        current = self._configurations.get_current(tax_profile_id)
        if current is None or current.organization_id != organization_id:
            raise MexicoTaxConfigurationNotFound("Mexico tax configuration not found.")
        return current

    def list_versions(self, organization_id: UUID, tax_profile_id: UUID):
        rows = self._configurations.list_versions(tax_profile_id)
        return [row for row in rows if row.organization_id == organization_id]
