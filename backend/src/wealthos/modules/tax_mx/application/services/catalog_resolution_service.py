"""Validate Mexico tax catalog entries against configuration context."""

from __future__ import annotations

from datetime import date

from wealthos.modules.tax_mx.domain.exceptions import MexicoTaxRegimeInvalid
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_catalog_repository import (
    MexicoTaxCatalogRepository,
)


class CatalogResolutionService:
    def __init__(self, catalogs: MexicoTaxCatalogRepository) -> None:
        self._catalogs = catalogs

    def validate_regime(
        self,
        *,
        regime_code: str,
        person_type: str,
        on_date: date | None = None,
    ) -> dict:
        if self._catalogs.is_empty():
            from wealthos.modules.tax_mx.catalogs.import_catalog import import_catalog

            import_catalog()
        entry = self._catalogs.get_entry("tax_regimes", regime_code, on_date=on_date)
        if entry is None:
            raise MexicoTaxRegimeInvalid(f"Tax regime {regime_code!r} is not in catalog.")
        expected = entry.get("person_type")
        if expected is not None and expected != person_type:
            raise MexicoTaxRegimeInvalid(
                f"Regime {regime_code!r} is not valid for person type {person_type!r}."
            )
        return entry

    def resolve_vat_rate(self, rate_code: str, *, on_date: date | None = None) -> dict:
        entry = self._catalogs.get_entry("vat_rates", rate_code, on_date=on_date)
        if entry is None:
            raise MexicoTaxRegimeInvalid(f"VAT rate {rate_code!r} is not in catalog.")
        return entry
