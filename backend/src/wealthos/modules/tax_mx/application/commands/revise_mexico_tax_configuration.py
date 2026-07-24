"""ReviseMexicoTaxConfiguration — close current and open a new version."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from wealthos.modules.tax_mx.application.commands.create_mexico_tax_configuration import (
    CreateMexicoTaxConfigurationCommand,
    CreateMexicoTaxConfigurationInput,
)
from wealthos.modules.tax_mx.domain.entities.mexico_tax_configuration import (
    MexicoTaxConfiguration,
)
from wealthos.modules.tax_mx.domain.exceptions import MexicoTaxConfigurationNotFound
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_configuration_repository import (
    MexicoTaxConfigurationRepository,
)


@dataclass(frozen=True, slots=True)
class ReviseMexicoTaxConfigurationInput:
    organization_id: UUID
    tax_profile_id: UUID
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


class ReviseMexicoTaxConfigurationCommand:
    def __init__(
        self,
        configurations: MexicoTaxConfigurationRepository,
        create_command: CreateMexicoTaxConfigurationCommand,
    ) -> None:
        self._configurations = configurations
        self._create = create_command

    def execute(self, data: ReviseMexicoTaxConfigurationInput) -> MexicoTaxConfiguration:
        current = self._configurations.get_current(data.tax_profile_id)
        if current is None:
            raise MexicoTaxConfigurationNotFound("No open configuration to revise.")
        close_on = data.effective_from - timedelta(days=1)
        current.close(close_on)
        self._configurations.save(current)
        return self._create.execute(
            CreateMexicoTaxConfigurationInput(
                organization_id=data.organization_id,
                tax_profile_id=data.tax_profile_id,
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
        )
