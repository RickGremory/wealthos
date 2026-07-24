"""Load Mexico tax catalogs from bundled JSON."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from wealthos.core.database import SessionLocal
from wealthos.modules.tax_mx.infrastructure.repositories import SqlAlchemyMexicoTaxCatalogRepository

_DATA_FILE = Path(__file__).resolve().parent / "data" / "catalogs-v1.json"


def load_catalog_entries(data: dict) -> list[dict]:
    version = data.get("catalog_version", "v1")
    entries: list[dict] = []
    for item in data.get("tax_regimes", []):
        entries.append(
            {
                "catalog_name": "tax_regimes",
                "catalog_version": version,
                "code": item["code"],
                "name": item["name"],
                "person_type": item.get("person_type"),
                "valid_from": date.fromisoformat(item["valid_from"]),
                "valid_to": (
                    date.fromisoformat(item["valid_to"]) if item.get("valid_to") else None
                ),
                "source_reference": "catalogs-v1.json",
            }
        )
    for item in data.get("vat_rates", []):
        entries.append(
            {
                "catalog_name": "vat_rates",
                "catalog_version": version,
                "code": item["code"],
                "name": item["name"],
                "rate": Decimal(str(item["rate"])) if item.get("rate") is not None else None,
                "valid_from": date.fromisoformat(item["valid_from"]),
                "valid_to": (
                    date.fromisoformat(item["valid_to"]) if item.get("valid_to") else None
                ),
                "source_reference": "catalogs-v1.json",
            }
        )
    for item in data.get("withholding_types", []):
        entries.append(
            {
                "catalog_name": "withholding_types",
                "catalog_version": version,
                "code": item["code"],
                "name": item["name"],
                "valid_from": date.fromisoformat(item["valid_from"]),
                "valid_to": (
                    date.fromisoformat(item["valid_to"]) if item.get("valid_to") else None
                ),
                "source_reference": "catalogs-v1.json",
            }
        )
    return entries


def import_catalog(*, data_path: Path | None = None) -> int:
    path = data_path or _DATA_FILE
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = load_catalog_entries(payload)
    with SessionLocal() as session:
        repo = SqlAlchemyMexicoTaxCatalogRepository(session)
        count = repo.upsert_entries(entries)
        session.commit()
        return count


def main() -> None:
    loaded = import_catalog()
    print(f"Loaded {loaded} catalog entries from {_DATA_FILE.name}")


if __name__ == "__main__":
    main()
