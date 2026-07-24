"""ListUnclassified query."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from wealthos.modules.tax_mx.application.services.mexico_tax_calculation_service import (
    MexicoTaxTransactionView,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_read_repository import (
    MexicoTaxReadRepository,
)
from wealthos.modules.taxes.domain.exceptions import TaxProfileNotFound
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)


@dataclass(frozen=True, slots=True)
class UnclassifiedPage:
    items: list[MexicoTaxTransactionView]
    total: int


class ListUnclassifiedQuery:
    def __init__(
        self,
        profiles: TaxProfileRepository,
        read: MexicoTaxReadRepository,
    ) -> None:
        self._profiles = profiles
        self._read = read

    def execute(
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
    ) -> UnclassifiedPage:
        profile = self._profiles.get_by_id(organization_id, tax_profile_id)
        if profile is None:
            raise TaxProfileNotFound("Tax profile not found.")
        items, total = self._read.get_unclassified_transactions(
            organization_id,
            tax_profile_id,
            date_from=date_from,
            date_to=date_to,
            transaction_type=transaction_type,
            category_id=category_id,
            account_id=account_id,
            limit=limit,
            offset=offset,
        )
        return UnclassifiedPage(items=items, total=total)
