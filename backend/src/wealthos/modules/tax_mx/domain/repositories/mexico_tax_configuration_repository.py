"""Persistence port for MexicoTaxConfiguration."""

from __future__ import annotations

from datetime import date
from typing import Protocol
from uuid import UUID

from wealthos.modules.tax_mx.domain.entities.mexico_tax_configuration import (
    MexicoTaxConfiguration,
)


class MexicoTaxConfigurationRepository(Protocol):
    def add(self, configuration: MexicoTaxConfiguration) -> MexicoTaxConfiguration: ...

    def get_by_id(
        self, organization_id: UUID, configuration_id: UUID
    ) -> MexicoTaxConfiguration | None: ...

    def get_applicable(
        self, tax_profile_id: UUID, target_date: date
    ) -> MexicoTaxConfiguration | None: ...

    def get_current(self, tax_profile_id: UUID) -> MexicoTaxConfiguration | None: ...

    def list_versions(self, tax_profile_id: UUID) -> list[MexicoTaxConfiguration]: ...

    def get_next_version(self, tax_profile_id: UUID) -> int: ...

    def save(self, configuration: MexicoTaxConfiguration) -> MexicoTaxConfiguration: ...

    def has_overlap(
        self,
        tax_profile_id: UUID,
        effective_from: date,
        effective_to: date | None,
        *,
        exclude_id: UUID | None = None,
    ) -> bool: ...
