"""ListMexicoTaxCatalogs query."""

from __future__ import annotations

from datetime import date

from wealthos.modules.tax_mx.catalogs.import_catalog import import_catalog
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_catalog_repository import (
    MexicoTaxCatalogRepository,
)


class ListMexicoTaxCatalogsQuery:
    CATALOGS = ("tax_regimes", "vat_rates", "withholding_types")

    def __init__(self, catalogs: MexicoTaxCatalogRepository) -> None:
        self._catalogs = catalogs

    def execute(self, *, on_date: date | None = None) -> dict[str, list[dict]]:
        if self._catalogs.is_empty():
            import_catalog()
        target = on_date or date.today()
        return {name: self._catalogs.list_catalog(name, on_date=target) for name in self.CATALOGS}
