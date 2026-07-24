"""CreateTaxProfile command."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.taxes.domain.entities.tax_profile import TaxProfile
from wealthos.modules.taxes.domain.exceptions import (
    TaxProfileAlreadyActive,
    TaxReserveAccountInvalid,
)
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)


@dataclass(frozen=True, slots=True)
class CreateTaxProfileInput:
    organization_id: UUID
    country_code: str
    taxpayer_type: str
    filing_frequency: str
    currency: str
    fiscal_year_start_month: int = 1
    jurisdiction: str | None = None
    tax_regime: str | None = None
    reserve_account_id: UUID | None = None


class CreateTaxProfileCommand:
    def __init__(
        self,
        profiles: TaxProfileRepository,
        accounts: AccountRepository,
    ) -> None:
        self._profiles = profiles
        self._accounts = accounts

    def execute(self, data: CreateTaxProfileInput) -> TaxProfile:
        if self._profiles.get_active(data.organization_id) is not None:
            raise TaxProfileAlreadyActive("Organization already has an active tax profile.")

        if data.reserve_account_id is not None:
            self._validate_reserve_account(
                data.organization_id,
                data.reserve_account_id,
                data.currency,
            )

        profile = TaxProfile.create(
            organization_id=data.organization_id,
            country_code=data.country_code,
            taxpayer_type=data.taxpayer_type,
            filing_frequency=data.filing_frequency,
            currency=data.currency,
            fiscal_year_start_month=data.fiscal_year_start_month,
            jurisdiction=data.jurisdiction,
            tax_regime=data.tax_regime,
            reserve_account_id=data.reserve_account_id,
        )
        return self._profiles.add(profile)

    def _validate_reserve_account(
        self,
        organization_id: UUID,
        account_id: UUID,
        currency: str,
    ) -> None:
        account = self._accounts.get_by_id(organization_id, account_id)
        if account is None or not account.is_active:
            raise TaxReserveAccountInvalid("Reserve account not found or inactive.")
        if not account.account_type.is_asset:
            raise TaxReserveAccountInvalid("Reserve account must be an asset account.")
        if account.currency.value != currency.upper():
            raise TaxReserveAccountInvalid("Reserve account currency must match profile currency.")
