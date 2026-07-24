"""Map TaxProfile ↔ TaxProfileModel."""

from __future__ import annotations

from wealthos.modules.taxes.domain.entities.tax_profile import TaxProfile
from wealthos.modules.taxes.domain.value_objects.country_code import CountryCode
from wealthos.modules.taxes.domain.value_objects.filing_frequency import FilingFrequency
from wealthos.modules.taxes.domain.value_objects.taxpayer_type import TaxpayerType
from wealthos.modules.taxes.infrastructure.models.tax_models import TaxProfileModel
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.currency import Currency


class TaxProfileMapper(BaseMapper[TaxProfileModel, TaxProfile]):
    def to_entity(self, model: TaxProfileModel) -> TaxProfile:
        return TaxProfile(
            id=model.id,
            organization_id=model.organization_id,
            country_code=CountryCode(model.country_code),
            jurisdiction=model.jurisdiction,
            taxpayer_type=TaxpayerType(model.taxpayer_type),
            tax_regime=model.tax_regime,
            filing_frequency=FilingFrequency(model.filing_frequency),
            fiscal_year_start_month=model.fiscal_year_start_month,
            currency=Currency(model.currency),
            reserve_account_id=model.reserve_account_id,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def to_model(self, entity: TaxProfile) -> TaxProfileModel:
        return TaxProfileModel(
            id=entity.id,
            organization_id=entity.organization_id,
            country_code=entity.country_code.value,
            jurisdiction=entity.jurisdiction,
            taxpayer_type=entity.taxpayer_type.value,
            tax_regime=entity.tax_regime,
            filing_frequency=entity.filing_frequency.value,
            fiscal_year_start_month=entity.fiscal_year_start_month,
            currency=entity.currency.value,
            reserve_account_id=entity.reserve_account_id,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def apply_to_model(self, entity: TaxProfile, model: TaxProfileModel) -> TaxProfileModel:
        model.jurisdiction = entity.jurisdiction
        model.tax_regime = entity.tax_regime
        model.filing_frequency = entity.filing_frequency.value
        model.fiscal_year_start_month = entity.fiscal_year_start_month
        model.reserve_account_id = entity.reserve_account_id
        model.is_active = entity.is_active
        model.updated_at = entity.updated_at
        return model
