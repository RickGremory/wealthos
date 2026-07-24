"""TaxCategoryMapping — category-level tax treatment override."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.taxes.domain.value_objects.percentage import Percentage
from wealthos.modules.taxes.domain.value_objects.tax_treatment import TaxTreatment


@dataclass(slots=True)
class TaxCategoryMapping:
    id: UUID
    organization_id: UUID
    tax_profile_id: UUID
    category_id: UUID
    tax_treatment: TaxTreatment
    deductibility_percentage: Percentage
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        tax_profile_id: UUID,
        category_id: UUID,
        tax_treatment: str,
        deductibility_percentage: Decimal | str = Decimal("100"),
        mapping_id: UUID | None = None,
    ) -> TaxCategoryMapping:
        now = datetime.now(UTC)
        return cls(
            id=mapping_id or uuid4(),
            organization_id=organization_id,
            tax_profile_id=tax_profile_id,
            category_id=category_id,
            tax_treatment=TaxTreatment(tax_treatment),
            deductibility_percentage=Percentage(
                deductibility_percentage,
                max_value=Decimal("100"),
            ),
            created_at=now,
            updated_at=now,
        )

    def update(
        self,
        *,
        tax_treatment: str,
        deductibility_percentage: Decimal | str,
    ) -> None:
        self.tax_treatment = TaxTreatment(tax_treatment)
        self.deductibility_percentage = Percentage(
            deductibility_percentage,
            max_value=Decimal("100"),
        )
        self.updated_at = datetime.now(UTC)
