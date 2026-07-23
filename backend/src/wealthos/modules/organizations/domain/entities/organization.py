"""Organization aggregate — financial workspace root for WealthOS."""

from __future__ import annotations

from wealthos.modules.organizations.domain.value_objects.currency import Currency
from wealthos.modules.organizations.domain.value_objects.locale import Locale
from wealthos.modules.organizations.domain.value_objects.name import Name
from wealthos.modules.organizations.domain.value_objects.slug import Slug
from wealthos.modules.organizations.domain.value_objects.timezone import Timezone


class Organization:
    """Rich domain entity representing a financial workspace.

    Identity (database id) is an infrastructure concern — the domain tracks
    business attributes and invariants only.
    """

    def __init__(
        self,
        *,
        name: Name,
        slug: Slug,
        currency: Currency,
        timezone: Timezone,
        locale: Locale,
    ) -> None:
        self._name = name
        self._slug = slug
        self._currency = currency
        self._timezone = timezone
        self._locale = locale

    @classmethod
    def create(
        cls,
        *,
        name: str,
        slug: str,
        currency: str = "MXN",
        timezone: str = "America/Mexico_City",
        locale: str = "es_MX",
    ) -> Organization:
        """Factory that validates primitives into value objects."""
        return cls(
            name=Name(name),
            slug=Slug(slug),
            currency=Currency(currency),
            timezone=Timezone(timezone),
            locale=Locale(locale),
        )

    @property
    def name(self) -> Name:
        return self._name

    @property
    def slug(self) -> Slug:
        return self._slug

    @property
    def currency(self) -> Currency:
        return self._currency

    @property
    def timezone(self) -> Timezone:
        return self._timezone

    @property
    def locale(self) -> Locale:
        return self._locale

    def rename(self, name: Name | str) -> None:
        self._name = name if isinstance(name, Name) else Name(name)

    def change_currency(self, currency: Currency | str) -> None:
        self._currency = currency if isinstance(currency, Currency) else Currency(currency)

    def change_timezone(self, timezone: Timezone | str) -> None:
        self._timezone = timezone if isinstance(timezone, Timezone) else Timezone(timezone)

    def change_locale(self, locale: Locale | str) -> None:
        self._locale = locale if isinstance(locale, Locale) else Locale(locale)

    def __repr__(self) -> str:
        return (
            f"Organization(name={self._name!r}, slug={self._slug!r}, currency={self._currency!r})"
        )
