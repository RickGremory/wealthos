"""Map TaxEvidence."""

from __future__ import annotations

from wealthos.modules.tax_mx.domain.entities.tax_evidence import TaxEvidence
from wealthos.modules.tax_mx.domain.value_objects.evidence_status import (
    EvidenceSource,
    EvidenceValidationStatus,
    TaxEvidenceType,
)
from wealthos.modules.tax_mx.infrastructure.models.tax_mx_models import TaxEvidenceModel
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.money import Money


class TaxEvidenceMapper(BaseMapper[TaxEvidenceModel, TaxEvidence]):
    def to_entity(self, model: TaxEvidenceModel) -> TaxEvidence:
        currency = model.currency or "MXN"
        return TaxEvidence(
            id=model.id,
            organization_id=model.organization_id,
            transaction_id=model.transaction_id,
            evidence_type=TaxEvidenceType(model.evidence_type),
            external_reference=model.external_reference,
            issuer_rfc=model.issuer_rfc,
            receiver_rfc=model.receiver_rfc,
            document_date=model.document_date,
            subtotal=Money(model.subtotal, currency) if model.subtotal is not None else None,
            tax_amount=Money(model.tax_amount, currency) if model.tax_amount is not None else None,
            total=Money(model.total, currency) if model.total is not None else None,
            validation_status=EvidenceValidationStatus(model.validation_status),
            source=EvidenceSource(model.source),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def to_model(self, entity: TaxEvidence) -> TaxEvidenceModel:
        currency = None
        if entity.total is not None:
            currency = entity.total.currency.value
        elif entity.subtotal is not None:
            currency = entity.subtotal.currency.value
        return TaxEvidenceModel(
            id=entity.id,
            organization_id=entity.organization_id,
            transaction_id=entity.transaction_id,
            evidence_type=entity.evidence_type.value,
            external_reference=entity.external_reference,
            issuer_rfc=entity.issuer_rfc,
            receiver_rfc=entity.receiver_rfc,
            document_date=entity.document_date,
            subtotal=entity.subtotal.amount if entity.subtotal else None,
            tax_amount=entity.tax_amount.amount if entity.tax_amount else None,
            total=entity.total.amount if entity.total else None,
            currency=currency,
            validation_status=entity.validation_status.value,
            source=entity.source.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def apply_to_model(self, entity: TaxEvidence, model: TaxEvidenceModel) -> TaxEvidenceModel:
        model.validation_status = entity.validation_status.value
        model.updated_at = entity.updated_at
        return model
