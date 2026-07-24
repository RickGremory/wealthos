"""Read model port for Mexico tax calculations."""

from __future__ import annotations

from datetime import date, datetime
from typing import Protocol
from uuid import UUID

from wealthos.modules.tax_mx.application.services.mexico_tax_calculation_service import (
    MexicoTaxTransactionView,
)


class MexicoTaxReadRepository(Protocol):
    def get_period_transactions(
        self,
        organization_id: UUID,
        *,
        date_from: date,
        date_to: date,
        currency: str | None = None,
    ) -> list[MexicoTaxTransactionView]: ...

    def get_unclassified_transactions(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        transaction_type: str | None = None,
        category_id: UUID | None = None,
        account_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[MexicoTaxTransactionView], int]: ...

    def latest_relevant_change_at(
        self,
        organization_id: UUID,
        *,
        date_from: date,
        date_to: date,
    ) -> datetime | None: ...
