"""TaxTransactionOverride — transaction-level tax treatment override."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.taxes.domain.value_objects.percentage import Percentage
from wealthos.modules.taxes.domain.value_objects.tax_treatment import TaxTreatment


@dataclass(slots=True)
class TaxTransactionOverride:
    id: UUID
    organization_id: UUID
    tax_profile_id: UUID
    transaction_id: UUID
    tax_treatment: TaxTreatment
    deductibility_percentage: Percentage
    reason: str | None
    created_by_user_id: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        tax_profile_id: UUID,
        transaction_id: UUID,
        tax_treatment: str,
        created_by_user_id: UUID,
        deductibility_percentage: Decimal | str = Decimal("100"),
        reason: str | None = None,
        override_id: UUID | None = None,
    ) -> TaxTransactionOverride:
        now = datetime.now(UTC)
        return cls(
            id=override_id or uuid4(),
            organization_id=organization_id,
            tax_profile_id=tax_profile_id,
            transaction_id=transaction_id,
            tax_treatment=TaxTreatment(tax_treatment),
            deductibility_percentage=Percentage(
                deductibility_percentage,
                max_value=Decimal("100"),
            ),
            reason=reason.strip() if reason else None,
            created_by_user_id=created_by_user_id,
            created_at=now,
            updated_at=now,
        )

    def update(
        self,
        *,
        tax_treatment: str,
        deductibility_percentage: Decimal | str,
        reason: str | None = None,
    ) -> None:
        self.tax_treatment = TaxTreatment(tax_treatment)
        self.deductibility_percentage = Percentage(
            deductibility_percentage,
            max_value=Decimal("100"),
        )
        self.reason = reason.strip() if reason else None
        self.updated_at = datetime.now(UTC)
