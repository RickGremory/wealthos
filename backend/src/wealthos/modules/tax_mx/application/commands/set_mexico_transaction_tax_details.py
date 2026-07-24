"""SetMexicoTransactionTaxDetails command."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from wealthos.modules.tax_mx.domain.entities.tax_evidence import MexicoTransactionTaxDetails
from wealthos.modules.tax_mx.domain.exceptions import MexicoTransactionNotFound
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_details_repository import (
    MexicoTaxDetailsRepository,
)
from wealthos.modules.transactions.domain.repositories.transaction_repository import (
    TransactionRepository,
)
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class SetMexicoTransactionTaxDetailsInput:
    organization_id: UUID
    transaction_id: UUID
    subtotal: Decimal
    vat_amount: Decimal
    total: Decimal
    currency: str
    withheld_income_tax: Decimal = Decimal("0")
    withheld_vat: Decimal = Decimal("0")
    other_taxes: Decimal = Decimal("0")
    calculation_source: str = "manual"


class SetMexicoTransactionTaxDetailsCommand:
    def __init__(
        self,
        transactions: TransactionRepository,
        details: MexicoTaxDetailsRepository,
    ) -> None:
        self._transactions = transactions
        self._details = details

    def execute(self, data: SetMexicoTransactionTaxDetailsInput) -> MexicoTransactionTaxDetails:
        tx = self._transactions.get_by_id(data.organization_id, data.transaction_id)
        if tx is None:
            raise MexicoTransactionNotFound("Transaction not found.")

        entity = MexicoTransactionTaxDetails.create(
            organization_id=data.organization_id,
            transaction_id=data.transaction_id,
            subtotal=Money(data.subtotal, data.currency),
            vat_amount=Money(data.vat_amount, data.currency),
            total=Money(data.total, data.currency),
            withheld_income_tax=Money(data.withheld_income_tax, data.currency),
            withheld_vat=Money(data.withheld_vat, data.currency),
            other_taxes=Money(data.other_taxes, data.currency),
            calculation_source=data.calculation_source,
        )
        return self._details.upsert(entity)
