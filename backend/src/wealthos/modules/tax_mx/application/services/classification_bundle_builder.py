"""Build ClassificationBundle for Mexico tax calculation."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from wealthos.modules.tax_mx.application.services.mexico_tax_calculation_service import (
    ClassificationBundle,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_category_mapping_repository import (
    MexicoTaxCategoryMappingRepository,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_details_repository import (
    MexicoTaxDetailsRepository,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_transaction_override_repository import (
    MexicoTaxTransactionOverrideRepository,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_withholding_repository import (
    MexicoTaxWithholdingRepository,
)
from wealthos.modules.tax_mx.domain.repositories.tax_evidence_repository import (
    TaxEvidenceRepository,
)


def build_mexico_classification_bundle(
    *,
    organization_id: UUID,
    tax_profile_id: UUID,
    transaction_ids: list[UUID],
    mappings: MexicoTaxCategoryMappingRepository,
    overrides: MexicoTaxTransactionOverrideRepository,
    details: MexicoTaxDetailsRepository,
    evidence: TaxEvidenceRepository,
    withholdings: MexicoTaxWithholdingRepository,
) -> ClassificationBundle:
    mapping_rows = mappings.list_by_profile(organization_id, tax_profile_id)
    override_rows = overrides.list_by_profile(organization_id, tax_profile_id)
    detail_rows = details.list_by_transactions(organization_id, transaction_ids)
    evidence_status = evidence.latest_status_by_transactions(organization_id, transaction_ids)
    withholding_rows = withholdings.list_by_transactions(organization_id, transaction_ids)

    withholdings_isr: dict[UUID, Decimal] = {}
    withholdings_vat: dict[UUID, Decimal] = {}
    for row in withholding_rows:
        if row.withholding_type.value == "income_tax":
            withholdings_isr[row.transaction_id] = (
                withholdings_isr.get(row.transaction_id, Decimal("0")) + row.amount.amount
            )
        elif row.withholding_type.value == "vat":
            withholdings_vat[row.transaction_id] = (
                withholdings_vat.get(row.transaction_id, Decimal("0")) + row.amount.amount
            )

    return ClassificationBundle(
        mappings={m.category_id: m for m in mapping_rows},
        overrides={o.transaction_id: o for o in override_rows},
        details={d.transaction_id: d for d in detail_rows},
        evidence_status_by_tx=evidence_status,
        withholdings_income_tax=withholdings_isr,
        withholdings_vat=withholdings_vat,
    )
