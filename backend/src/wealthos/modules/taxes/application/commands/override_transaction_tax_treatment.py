"""OverrideTransactionTaxTreatment command."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from wealthos.modules.taxes.domain.entities.tax_transaction_override import (
    TaxTransactionOverride,
)
from wealthos.modules.taxes.domain.exceptions import (
    TaxProfileNotFound,
    TaxTransactionNotFound,
)
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_transaction_override_repository import (
    TaxTransactionOverrideRepository,
)
from wealthos.modules.transactions.domain.repositories.transaction_repository import (
    TransactionRepository,
)


@dataclass(frozen=True, slots=True)
class OverrideTransactionTaxTreatmentInput:
    organization_id: UUID
    tax_profile_id: UUID
    transaction_id: UUID
    tax_treatment: str
    created_by_user_id: UUID
    deductibility_percentage: Decimal = Decimal("100")
    reason: str | None = None


class OverrideTransactionTaxTreatmentCommand:
    def __init__(
        self,
        profiles: TaxProfileRepository,
        transactions: TransactionRepository,
        overrides: TaxTransactionOverrideRepository,
    ) -> None:
        self._profiles = profiles
        self._transactions = transactions
        self._overrides = overrides

    def execute(self, data: OverrideTransactionTaxTreatmentInput) -> TaxTransactionOverride:
        profile = self._profiles.get_by_id(data.organization_id, data.tax_profile_id)
        if profile is None:
            raise TaxProfileNotFound("Tax profile not found.")

        transaction = self._transactions.get_by_id(data.organization_id, data.transaction_id)
        if transaction is None:
            raise TaxTransactionNotFound("Transaction not found.")

        override = TaxTransactionOverride.create(
            organization_id=data.organization_id,
            tax_profile_id=data.tax_profile_id,
            transaction_id=data.transaction_id,
            tax_treatment=data.tax_treatment,
            created_by_user_id=data.created_by_user_id,
            deductibility_percentage=data.deductibility_percentage,
            reason=data.reason,
        )
        return self._overrides.upsert(override)
