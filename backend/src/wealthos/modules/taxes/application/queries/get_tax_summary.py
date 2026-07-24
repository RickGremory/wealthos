"""GetTaxSummary query."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.taxes.application.services.tax_period_generator import (
    TaxPeriodGenerator,
)
from wealthos.modules.taxes.domain.repositories.tax_calculation_repository import (
    TaxCalculationRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_payment_repository import (
    TaxPaymentRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_period_repository import (
    TaxPeriodRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_read_repository import TaxReadRepository

_ZERO = Decimal("0.00")
_CASH_LIKE = frozenset({"checking", "savings", "cash", "digital_wallet"})


@dataclass(frozen=True, slots=True)
class TaxSummaryByCurrency:
    currency: str
    estimated_tax: Decimal
    paid: Decimal
    balance: Decimal
    reserve_balance: Decimal
    cash_like_assets: Decimal
    available_after_tax: Decimal


@dataclass(frozen=True, slots=True)
class TaxSummary:
    has_active_profile: bool
    current_period_id: UUID | None
    by_currency: tuple[TaxSummaryByCurrency, ...]


class GetTaxSummaryQuery:
    def __init__(
        self,
        profiles: TaxProfileRepository,
        periods: TaxPeriodRepository,
        calculations: TaxCalculationRepository,
        payments: TaxPaymentRepository,
        read: TaxReadRepository,
        accounts: AccountRepository,
        period_generator: TaxPeriodGenerator | None = None,
    ) -> None:
        self._profiles = profiles
        self._periods = periods
        self._calculations = calculations
        self._payments = payments
        self._read = read
        self._accounts = accounts
        self._period_generator = period_generator or TaxPeriodGenerator(periods)

    def execute(self, organization_id: UUID) -> TaxSummary:
        profile = self._profiles.get_active(organization_id)
        if profile is None:
            return TaxSummary(has_active_profile=False, current_period_id=None, by_currency=())

        current = self._period_generator.ensure_current_period(profile)
        latest = self._calculations.get_latest_by_period(organization_id, current.id)
        currency = profile.currency.value
        estimated = latest.estimated_tax.amount if latest else _ZERO
        paid = self._payments.sum_by_period(
            organization_id,
            current.id,
            currency=currency,
        )
        balance = max(estimated - paid, _ZERO)
        reserve = _ZERO
        if profile.reserve_account_id is not None:
            reserve_balance = self._read.get_reserve_account_balance(
                organization_id,
                profile.reserve_account_id,
            )
            reserve = reserve_balance if reserve_balance is not None else _ZERO

        cash_like = self._cash_like_assets(organization_id, currency)
        available = max(cash_like - balance, _ZERO)

        return TaxSummary(
            has_active_profile=True,
            current_period_id=current.id,
            by_currency=(
                TaxSummaryByCurrency(
                    currency=currency,
                    estimated_tax=estimated,
                    paid=paid,
                    balance=balance,
                    reserve_balance=reserve,
                    cash_like_assets=cash_like,
                    available_after_tax=available,
                ),
            ),
        )

    def _cash_like_assets(self, organization_id: UUID, currency: str) -> Decimal:
        total = _ZERO
        for account in self._accounts.list_by_organization(organization_id):
            if not account.is_active:
                continue
            if account.account_type.value not in _CASH_LIKE:
                continue
            if account.currency.value != currency:
                continue
            total += account.current_balance.amount
        return total
