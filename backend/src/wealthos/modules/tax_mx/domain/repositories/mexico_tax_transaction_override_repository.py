"""Persistence port for Mexico transaction overrides."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.tax_mx.domain.entities.mexico_tax_classification import (
    MexicoTaxTransactionOverride,
)


class MexicoTaxTransactionOverrideRepository(Protocol):
    def add(self, override: MexicoTaxTransactionOverride) -> MexicoTaxTransactionOverride: ...

    def get_by_transaction(
        self, organization_id: UUID, tax_profile_id: UUID, transaction_id: UUID
    ) -> MexicoTaxTransactionOverride | None: ...

    def list_by_profile(
        self, organization_id: UUID, tax_profile_id: UUID
    ) -> list[MexicoTaxTransactionOverride]: ...

    def save(self, override: MexicoTaxTransactionOverride) -> MexicoTaxTransactionOverride: ...
