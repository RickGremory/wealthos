"""Persistence port for TaxProfile aggregates."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.taxes.domain.entities.tax_profile import TaxProfile


class TaxProfileRepository(Protocol):
    def add(self, profile: TaxProfile) -> TaxProfile: ...

    def get_by_id(self, organization_id: UUID, profile_id: UUID) -> TaxProfile | None: ...

    def get_active(self, organization_id: UUID) -> TaxProfile | None: ...

    def list_by_organization(self, organization_id: UUID) -> list[TaxProfile]: ...

    def save(self, profile: TaxProfile) -> TaxProfile: ...
