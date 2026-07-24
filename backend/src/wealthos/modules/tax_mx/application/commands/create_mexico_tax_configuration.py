"""CreateMexicoTaxConfiguration command."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from wealthos.modules.tax_mx.domain.entities.mexico_tax_configuration import (
    MexicoTaxConfiguration,
)
from wealthos.modules.tax_mx.domain.exceptions import (
    MexicoTaxConfigurationOverlap,
    MexicoTaxProfileIncompatible,
    MexicoTaxProfileRequired,
    MexicoTaxRegimeInvalid,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_catalog_repository import (
    MexicoTaxCatalogRepository,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_configuration_repository import (
    MexicoTaxConfigurationRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)


@dataclass(frozen=True, slots=True)
class CreateMexicoTaxConfigurationInput:
    organization_id: UUID
    rfc: str
    person_type: str
    tax_regime_code: str
    vat_enabled: bool
    income_tax_enabled: bool
    effective_from: date
    default_vat_rate: Decimal | None = None
    income_tax_estimation_method: str | None = None
    income_tax_estimation_base: str | None = None
    income_tax_estimation_rate: Decimal | None = None
    requires_invoice_evidence: bool = True
    tax_profile_id: UUID | None = None


class CreateMexicoTaxConfigurationCommand:
    def __init__(
        self,
        configurations: MexicoTaxConfigurationRepository,
        profiles: TaxProfileRepository,
        catalogs: MexicoTaxCatalogRepository,
    ) -> None:
        self._configurations = configurations
        self._profiles = profiles
        self._catalogs = catalogs

    def execute(self, data: CreateMexicoTaxConfigurationInput) -> MexicoTaxConfiguration:
        profile = None
        if data.tax_profile_id is not None:
            profile = self._profiles.get_by_id(data.organization_id, data.tax_profile_id)
        else:
            profile = self._profiles.get_active(data.organization_id)
        if profile is None:
            raise MexicoTaxProfileRequired("An active tax profile is required.")
        if profile.country_code.value != "MX":
            raise MexicoTaxProfileIncompatible("Tax profile country must be MX.")

        from wealthos.modules.tax_mx.domain.value_objects.mexico_person_type import (
            MexicoPersonType,
        )

        person = MexicoPersonType(data.person_type)
        if profile.taxpayer_type.value != person.to_taxpayer_type():
            raise MexicoTaxProfileIncompatible(
                "Mexico person_type is incompatible with tax profile taxpayer_type."
            )

        if self._catalogs.is_empty():
            from wealthos.modules.tax_mx.catalogs.import_catalog import import_catalog

            import_catalog()

        regime = self._catalogs.get_entry(
            "tax_regimes",
            data.tax_regime_code,
            on_date=data.effective_from,
        )
        if regime is None:
            raise MexicoTaxRegimeInvalid("Tax regime code is not valid in the active catalog.")
        if regime.get("person_type") and regime["person_type"] != person.value:
            raise MexicoTaxRegimeInvalid("Tax regime is not valid for this person type.")

        if self._configurations.has_overlap(profile.id, data.effective_from, None):
            raise MexicoTaxConfigurationOverlap(
                "Configuration effective range overlaps an existing version."
            )

        configuration = MexicoTaxConfiguration.create(
            organization_id=data.organization_id,
            tax_profile_id=profile.id,
            version=self._configurations.get_next_version(profile.id),
            rfc=data.rfc,
            person_type=data.person_type,
            tax_regime_code=data.tax_regime_code,
            vat_enabled=data.vat_enabled,
            income_tax_enabled=data.income_tax_enabled,
            effective_from=data.effective_from,
            default_vat_rate=data.default_vat_rate,
            income_tax_estimation_method=data.income_tax_estimation_method,
            income_tax_estimation_base=data.income_tax_estimation_base,
            income_tax_estimation_rate=data.income_tax_estimation_rate,
            requires_invoice_evidence=data.requires_invoice_evidence,
        )
        return self._configurations.add(configuration)
