"""Organization aggregate — financial workspace root for WealthOS."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from wealthos.modules.organizations.domain.value_objects.currency import Currency
from wealthos.modules.organizations.domain.value_objects.locale import Locale
from wealthos.modules.organizations.domain.value_objects.name import OrganizationName
from wealthos.modules.organizations.domain.value_objects.slug import OrganizationSlug
from wealthos.modules.organizations.domain.value_objects.timezone import Timezone


@dataclass(slots=True)
class Organization:
    """Rich domain entity representing a financial workspace.

    Identity is a domain UUID so the aggregate keeps the same identity
    across persistence technologies.
    """

    id: UUID
    name: OrganizationName
    slug: OrganizationSlug
    currency: Currency
    timezone: Timezone
    locale: Locale
    created_at: datetime
    updated_at: datetime
    debt_strategy: str = "avalanche"

    @classmethod
    def create(
        cls,
        *,
        name: str,
        slug: str,
        currency: str = "MXN",
        timezone: str = "America/Cancun",
        locale: str = "es-MX",
        debt_strategy: str = "avalanche",
        organization_id: UUID | None = None,
    ) -> Organization:
        """Factory that validates primitives into value objects."""
        now = datetime.now(UTC)
        strategy = debt_strategy.strip().lower()
        allowed = {"avalanche", "snowball", "minimum_only", "manual"}
        if strategy not in allowed:
            raise ValueError(f"debt_strategy must be one of: {', '.join(sorted(allowed))}")
        return cls(
            id=organization_id or uuid4(),
            name=OrganizationName(name),
            slug=OrganizationSlug(slug),
            currency=Currency(currency),
            timezone=Timezone(timezone),
            locale=Locale(locale),
            created_at=now,
            updated_at=now,
            debt_strategy=strategy,
        )

    def rename(self, name: OrganizationName | str) -> None:
        self.name = name if isinstance(name, OrganizationName) else OrganizationName(name)
        self.updated_at = datetime.now(UTC)

    def change_currency(self, currency: Currency | str) -> None:
        self.currency = currency if isinstance(currency, Currency) else Currency(currency)
        self.updated_at = datetime.now(UTC)

    def change_timezone(self, timezone: Timezone | str) -> None:
        self.timezone = timezone if isinstance(timezone, Timezone) else Timezone(timezone)
        self.updated_at = datetime.now(UTC)

    def change_locale(self, locale: Locale | str) -> None:
        self.locale = locale if isinstance(locale, Locale) else Locale(locale)
        self.updated_at = datetime.now(UTC)

    def change_debt_strategy(self, strategy: str) -> None:
        cleaned = strategy.strip().lower()
        allowed = {"avalanche", "snowball", "minimum_only", "manual"}
        if cleaned not in allowed:
            raise ValueError(f"debt_strategy must be one of: {', '.join(sorted(allowed))}")
        self.debt_strategy = cleaned
        self.updated_at = datetime.now(UTC)
