"""Persistence port for Mexico tax catalogs."""

from __future__ import annotations

from datetime import date
from typing import Protocol


class MexicoTaxCatalogRepository(Protocol):
    def list_catalog(self, catalog_name: str, *, on_date: date | None = None) -> list[dict]: ...

    def get_entry(
        self, catalog_name: str, code: str, *, on_date: date | None = None
    ) -> dict | None: ...

    def upsert_entries(self, entries: list[dict]) -> int: ...

    def is_empty(self) -> bool: ...
