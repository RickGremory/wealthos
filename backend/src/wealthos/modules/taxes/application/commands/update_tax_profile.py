"""UpdateTaxProfile command."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.taxes.domain.entities.tax_profile import TaxProfile
from wealthos.modules.taxes.domain.exceptions import (
    TaxProfileNotFound,
    TaxReserveAccountInvalid,
)
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)


@dataclass(frozen=True, slots=True)
class UpdateTaxProfileInput:
    organization_id: UUID
    profile_id: UUID
    jurisdiction: str | None = None
    tax_regime: str | None = None
    filing_frequency: str | None = None
    fiscal_year_start_month: int | None = None
    reserve_account_id: UUID | None = None
    clear_reserve_account: bool = False
    fields_set: frozenset[str] | None = None


class UpdateTaxProfileCommand:
    def __init__(
        self,
        profiles: TaxProfileRepository,
        accounts: AccountRepository,
    ) -> None:
        self._profiles = profiles
        self._accounts = accounts

    def execute(self, data: UpdateTaxProfileInput) -> TaxProfile:
        profile = self._profiles.get_by_id(data.organization_id, data.profile_id)
        if profile is None:
            raise TaxProfileNotFound("Tax profile not found.")

        fields = data.fields_set or frozenset()
        if data.clear_reserve_account or "reserve_account_id" in fields:
            reserve_id = None if data.clear_reserve_account else data.reserve_account_id
            if reserve_id is not None:
                self._validate_reserve_account(
                    data.organization_id,
                    reserve_id,
                    profile.currency.value,
                )

        profile.update(
            jurisdiction=data.jurisdiction,
            tax_regime=data.tax_regime,
            filing_frequency=data.filing_frequency,
            fiscal_year_start_month=data.fiscal_year_start_month,
            reserve_account_id=data.reserve_account_id,
            clear_reserve_account=data.clear_reserve_account,
            fields_set=fields,
        )
        return self._profiles.save(profile)

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
        if account.currency.value != currency:
            raise TaxReserveAccountInvalid("Reserve account currency must match profile currency.")
