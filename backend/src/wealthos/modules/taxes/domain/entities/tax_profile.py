"""TaxProfile aggregate — organization fiscal configuration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from wealthos.modules.taxes.domain.exceptions import InvalidFiscalYearStartMonth
from wealthos.modules.taxes.domain.value_objects.country_code import CountryCode
from wealthos.modules.taxes.domain.value_objects.filing_frequency import FilingFrequency
from wealthos.modules.taxes.domain.value_objects.taxpayer_type import TaxpayerType
from wealthos.shared.domain.value_objects.currency import Currency


@dataclass(slots=True)
class TaxProfile:
    id: UUID
    organization_id: UUID
    country_code: CountryCode
    jurisdiction: str | None
    taxpayer_type: TaxpayerType
    tax_regime: str | None
    filing_frequency: FilingFrequency
    fiscal_year_start_month: int
    currency: Currency
    reserve_account_id: UUID | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        country_code: str,
        taxpayer_type: str,
        filing_frequency: str,
        currency: str,
        fiscal_year_start_month: int = 1,
        jurisdiction: str | None = None,
        tax_regime: str | None = None,
        reserve_account_id: UUID | None = None,
        profile_id: UUID | None = None,
    ) -> TaxProfile:
        if fiscal_year_start_month < 1 or fiscal_year_start_month > 12:
            raise InvalidFiscalYearStartMonth("Fiscal year start month must be between 1 and 12.")
        now = datetime.now(UTC)
        return cls(
            id=profile_id or uuid4(),
            organization_id=organization_id,
            country_code=CountryCode(country_code),
            jurisdiction=jurisdiction.strip() if jurisdiction else None,
            taxpayer_type=TaxpayerType(taxpayer_type),
            tax_regime=tax_regime.strip() if tax_regime else None,
            filing_frequency=FilingFrequency(filing_frequency),
            fiscal_year_start_month=fiscal_year_start_month,
            currency=Currency(currency),
            reserve_account_id=reserve_account_id,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    def update(
        self,
        *,
        jurisdiction: str | None = None,
        tax_regime: str | None = None,
        filing_frequency: str | None = None,
        fiscal_year_start_month: int | None = None,
        reserve_account_id: UUID | None = None,
        clear_reserve_account: bool = False,
        fields_set: frozenset[str] | None = None,
    ) -> None:
        fields = fields_set or frozenset()
        if "jurisdiction" in fields:
            self.jurisdiction = jurisdiction.strip() if jurisdiction else None
        if "tax_regime" in fields:
            self.tax_regime = tax_regime.strip() if tax_regime else None
        if "filing_frequency" in fields and filing_frequency is not None:
            self.filing_frequency = FilingFrequency(filing_frequency)
        if "fiscal_year_start_month" in fields and fiscal_year_start_month is not None:
            if fiscal_year_start_month < 1 or fiscal_year_start_month > 12:
                raise InvalidFiscalYearStartMonth(
                    "Fiscal year start month must be between 1 and 12."
                )
            self.fiscal_year_start_month = fiscal_year_start_month
        if clear_reserve_account or "reserve_account_id" in fields:
            self.reserve_account_id = None if clear_reserve_account else reserve_account_id
        self.updated_at = datetime.now(UTC)

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now(UTC)
