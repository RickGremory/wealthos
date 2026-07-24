"""Persistence port for Mexico transaction tax details."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.tax_mx.domain.entities.tax_evidence import MexicoTransactionTaxDetails


class MexicoTaxDetailsRepository(Protocol):
    def add(self, details: MexicoTransactionTaxDetails) -> MexicoTransactionTaxDetails: ...

    def get_by_transaction(
        self, organization_id: UUID, transaction_id: UUID
    ) -> MexicoTransactionTaxDetails | None: ...

    def list_by_transactions(
        self, organization_id: UUID, transaction_ids: list[UUID]
    ) -> list[MexicoTransactionTaxDetails]: ...

    def save(self, details: MexicoTransactionTaxDetails) -> MexicoTransactionTaxDetails: ...

    def upsert(self, details: MexicoTransactionTaxDetails) -> MexicoTransactionTaxDetails: ...
