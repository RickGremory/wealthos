"""Classify a transaction with a Mexico tax override."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from wealthos.modules.tax_mx.domain.entities.mexico_tax_classification import (
    MexicoTaxTransactionOverride,
)
from wealthos.modules.tax_mx.domain.exceptions import (
    MexicoTaxProfileRequired,
    MexicoTransactionNotFound,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_transaction_override_repository import (
    MexicoTaxTransactionOverrideRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)
from wealthos.modules.transactions.domain.repositories.transaction_repository import (
    TransactionRepository,
)


@dataclass(frozen=True, slots=True)
class ClassifyMexicoTaxTransactionInput:
    organization_id: UUID
    tax_profile_id: UUID
    transaction_id: UUID
    vat_treatment: str
    created_by_user_id: UUID
    income_treatment: str | None = None
    expense_treatment: str | None = None
    deductibility_percentage: Decimal = Decimal("100")
    vat_creditable_percentage: Decimal = Decimal("100")
    requires_cfdi: bool = False
    reason: str | None = None


class ClassifyMexicoTaxTransactionCommand:
    def __init__(
        self,
        overrides: MexicoTaxTransactionOverrideRepository,
        profiles: TaxProfileRepository,
        transactions: TransactionRepository,
    ) -> None:
        self._overrides = overrides
        self._profiles = profiles
        self._transactions = transactions

    def execute(self, data: ClassifyMexicoTaxTransactionInput) -> MexicoTaxTransactionOverride:
        if self._profiles.get_by_id(data.organization_id, data.tax_profile_id) is None:
            raise MexicoTaxProfileRequired("Tax profile not found.")
        tx = self._transactions.get_by_id(data.organization_id, data.transaction_id)
        if tx is None:
            raise MexicoTransactionNotFound("Transaction not found.")

        existing = self._overrides.get_by_transaction(
            data.organization_id, data.tax_profile_id, data.transaction_id
        )
        if existing is not None:
            # Replace by creating a fresh override entity with same id fields via save path.
            replacement = MexicoTaxTransactionOverride.create(
                organization_id=data.organization_id,
                tax_profile_id=data.tax_profile_id,
                transaction_id=data.transaction_id,
                vat_treatment=data.vat_treatment,
                created_by_user_id=data.created_by_user_id,
                income_treatment=data.income_treatment,
                expense_treatment=data.expense_treatment,
                deductibility_percentage=data.deductibility_percentage,
                vat_creditable_percentage=data.vat_creditable_percentage,
                requires_cfdi=data.requires_cfdi,
                reason=data.reason,
                override_id=existing.id,
            )
            replacement.created_at = existing.created_at
            return self._overrides.save(replacement)

        override = MexicoTaxTransactionOverride.create(
            organization_id=data.organization_id,
            tax_profile_id=data.tax_profile_id,
            transaction_id=data.transaction_id,
            vat_treatment=data.vat_treatment,
            created_by_user_id=data.created_by_user_id,
            income_treatment=data.income_treatment,
            expense_treatment=data.expense_treatment,
            deductibility_percentage=data.deductibility_percentage,
            vat_creditable_percentage=data.vat_creditable_percentage,
            requires_cfdi=data.requires_cfdi,
            reason=data.reason,
        )
        return self._overrides.add(override)
