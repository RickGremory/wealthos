"""Map MexicoTaxConfiguration ↔ model."""

from __future__ import annotations

from wealthos.modules.tax_mx.domain.entities.mexico_tax_configuration import (
    MexicoTaxConfiguration,
)
from wealthos.modules.tax_mx.domain.value_objects.estimation import (
    IncomeTaxEstimationBase,
    IncomeTaxEstimationMethod,
)
from wealthos.modules.tax_mx.domain.value_objects.mexico_person_type import MexicoPersonType
from wealthos.modules.tax_mx.domain.value_objects.rfc import RFC
from wealthos.modules.tax_mx.infrastructure.models.tax_mx_models import (
    MexicoTaxConfigurationModel,
)
from wealthos.modules.taxes.domain.value_objects.percentage import Percentage
from wealthos.shared.base import BaseMapper


class MexicoTaxConfigurationMapper(BaseMapper[MexicoTaxConfigurationModel, MexicoTaxConfiguration]):
    def to_entity(self, model: MexicoTaxConfigurationModel) -> MexicoTaxConfiguration:
        return MexicoTaxConfiguration(
            id=model.id,
            organization_id=model.organization_id,
            tax_profile_id=model.tax_profile_id,
            version=model.version,
            rfc=RFC(model.rfc),
            person_type=MexicoPersonType(model.person_type),
            tax_regime_code=model.tax_regime_code,
            vat_enabled=model.vat_enabled,
            income_tax_enabled=model.income_tax_enabled,
            default_vat_rate=(
                Percentage(model.default_vat_rate) if model.default_vat_rate is not None else None
            ),
            income_tax_estimation_method=(
                IncomeTaxEstimationMethod(model.income_tax_estimation_method)
                if model.income_tax_estimation_method
                else None
            ),
            income_tax_estimation_base=(
                IncomeTaxEstimationBase(model.income_tax_estimation_base)
                if model.income_tax_estimation_base
                else None
            ),
            income_tax_estimation_rate=(
                Percentage(model.income_tax_estimation_rate)
                if model.income_tax_estimation_rate is not None
                else None
            ),
            cash_flow_basis=model.cash_flow_basis,
            requires_invoice_evidence=model.requires_invoice_evidence,
            effective_from=model.effective_from,
            effective_to=model.effective_to,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def to_model(self, entity: MexicoTaxConfiguration) -> MexicoTaxConfigurationModel:
        return MexicoTaxConfigurationModel(
            id=entity.id,
            organization_id=entity.organization_id,
            tax_profile_id=entity.tax_profile_id,
            version=entity.version,
            rfc=entity.rfc.value,
            person_type=entity.person_type.value,
            tax_regime_code=entity.tax_regime_code,
            vat_enabled=entity.vat_enabled,
            income_tax_enabled=entity.income_tax_enabled,
            default_vat_rate=(entity.default_vat_rate.value if entity.default_vat_rate else None),
            income_tax_estimation_method=(
                entity.income_tax_estimation_method.value
                if entity.income_tax_estimation_method
                else None
            ),
            income_tax_estimation_base=(
                entity.income_tax_estimation_base.value
                if entity.income_tax_estimation_base
                else None
            ),
            income_tax_estimation_rate=(
                entity.income_tax_estimation_rate.value
                if entity.income_tax_estimation_rate
                else None
            ),
            cash_flow_basis=entity.cash_flow_basis,
            requires_invoice_evidence=entity.requires_invoice_evidence,
            effective_from=entity.effective_from,
            effective_to=entity.effective_to,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def apply_to_model(
        self, entity: MexicoTaxConfiguration, model: MexicoTaxConfigurationModel
    ) -> MexicoTaxConfigurationModel:
        model.effective_to = entity.effective_to
        model.updated_at = entity.updated_at
        return model
