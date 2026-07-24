"""CalculateTaxPeriod command."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from wealthos.modules.taxes.application.services.classification_context_builder import (
    build_classification_context,
)
from wealthos.modules.taxes.application.services.tax_calculation_service import (
    TaxCalculationService,
)
from wealthos.modules.taxes.application.services.tax_period_generator import (
    TaxPeriodGenerator,
)
from wealthos.modules.taxes.domain.entities.tax_calculation import TaxCalculation
from wealthos.modules.taxes.domain.exceptions import TaxPeriodNotFound, TaxProfileNotFound
from wealthos.modules.taxes.domain.repositories.tax_calculation_repository import (
    TaxCalculationRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_category_mapping_repository import (
    TaxCategoryMappingRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_period_repository import (
    TaxPeriodRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_read_repository import TaxReadRepository
from wealthos.modules.taxes.domain.repositories.tax_rule_repository import TaxRuleRepository
from wealthos.modules.taxes.domain.repositories.tax_transaction_override_repository import (
    TaxTransactionOverrideRepository,
)


@dataclass(frozen=True, slots=True)
class CalculateTaxPeriodResult:
    calculation: TaxCalculation
    paid_amount: Decimal


class CalculateTaxPeriodCommand:
    def __init__(
        self,
        profiles: TaxProfileRepository,
        periods: TaxPeriodRepository,
        rules: TaxRuleRepository,
        calculations: TaxCalculationRepository,
        mappings: TaxCategoryMappingRepository,
        overrides: TaxTransactionOverrideRepository,
        read: TaxReadRepository,
        calculator: TaxCalculationService | None = None,
        period_generator: TaxPeriodGenerator | None = None,
    ) -> None:
        self._profiles = profiles
        self._periods = periods
        self._rules = rules
        self._calculations = calculations
        self._mappings = mappings
        self._overrides = overrides
        self._read = read
        self._calculator = calculator or TaxCalculationService()
        self._period_generator = period_generator or TaxPeriodGenerator(periods)

    def execute(
        self,
        organization_id: UUID,
        period_id: UUID,
        performed_by_user_id: UUID,
    ) -> CalculateTaxPeriodResult:
        period = self._periods.get_by_id(organization_id, period_id)
        if period is None:
            raise TaxPeriodNotFound("Tax period not found.")

        period = self._periods.lock_for_update(organization_id, period_id)
        assert period is not None
        period.ensure_can_calculate()

        profile = self._profiles.get_by_id(organization_id, period.tax_profile_id)
        if profile is None:
            raise TaxProfileNotFound("Tax profile not found.")

        self._period_generator.ensure_current_period(profile)

        rules = self._rules.list_active_for_period(
            organization_id,
            profile.id,
            period.date_from,
            period.date_to,
        )
        transactions = self._read.get_taxable_transactions(
            organization_id,
            date_from=period.date_from,
            date_to=period.date_to,
        )
        mapping_rows = self._mappings.list_by_profile(organization_id, profile.id)
        override_rows = self._overrides.list_by_profile(organization_id, profile.id)
        payments = self._read.get_period_payments(organization_id, period.id)
        context = build_classification_context(mapping_rows, override_rows)

        self._calculations.supersede_completed(period.id)
        version = self._calculations.get_next_version(period.id)

        calculation, paid = self._calculator.calculate(
            profile=profile,
            period_id=period.id,
            period_from=period.date_from,
            period_to=period.date_to,
            rules=rules,
            transactions=transactions,
            payments=payments,
            context=context,
            version=version,
            performed_by_user_id=performed_by_user_id,
        )
        stored = self._calculations.add(calculation)
        period.mark_calculated()
        self._periods.save(period)
        return CalculateTaxPeriodResult(calculation=stored, paid_amount=paid)
