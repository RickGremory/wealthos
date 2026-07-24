"""Persistence port for TaxEvidence."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.tax_mx.domain.entities.tax_evidence import TaxEvidence


class TaxEvidenceRepository(Protocol):
    def add(self, evidence: TaxEvidence) -> TaxEvidence: ...

    def list_by_transaction(
        self, organization_id: UUID, transaction_id: UUID
    ) -> list[TaxEvidence]: ...

    def latest_status_by_transactions(
        self, organization_id: UUID, transaction_ids: list[UUID]
    ) -> dict[UUID, str]: ...

    def save(self, evidence: TaxEvidence) -> TaxEvidence: ...
