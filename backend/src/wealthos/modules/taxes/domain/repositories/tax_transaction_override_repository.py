"""Persistence port for TaxTransactionOverride."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.taxes.domain.entities.tax_transaction_override import (
    TaxTransactionOverride,
)


class TaxTransactionOverrideRepository(Protocol):
    def upsert(self, override: TaxTransactionOverride) -> TaxTransactionOverride: ...

    def list_by_profile(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
    ) -> list[TaxTransactionOverride]: ...

    def get_by_transaction(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
        transaction_id: UUID,
    ) -> TaxTransactionOverride | None: ...
