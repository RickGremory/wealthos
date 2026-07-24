"""SQLAlchemy MexicoTaxCatalogRepository."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from wealthos.modules.tax_mx.infrastructure.models.tax_mx_models import MxTaxCatalogEntryModel


class SqlAlchemyMexicoTaxCatalogRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_catalog(self, catalog_name: str, *, on_date: date | None = None) -> list[dict]:
        target = on_date or date.today()
        stmt = select(MxTaxCatalogEntryModel).where(
            MxTaxCatalogEntryModel.catalog_name == catalog_name,
            MxTaxCatalogEntryModel.is_active.is_(True),
            MxTaxCatalogEntryModel.valid_from <= target,
            or_(
                MxTaxCatalogEntryModel.valid_to.is_(None),
                MxTaxCatalogEntryModel.valid_to >= target,
            ),
        )
        return [self._row(m) for m in self._session.scalars(stmt)]

    def get_entry(
        self, catalog_name: str, code: str, *, on_date: date | None = None
    ) -> dict | None:
        target = on_date or date.today()
        stmt = select(MxTaxCatalogEntryModel).where(
            MxTaxCatalogEntryModel.catalog_name == catalog_name,
            MxTaxCatalogEntryModel.code == code,
            MxTaxCatalogEntryModel.is_active.is_(True),
            MxTaxCatalogEntryModel.valid_from <= target,
            or_(
                MxTaxCatalogEntryModel.valid_to.is_(None),
                MxTaxCatalogEntryModel.valid_to >= target,
            ),
        )
        model = self._session.scalars(stmt).first()
        return self._row(model) if model else None

    def upsert_entries(self, entries: list[dict]) -> int:
        count = 0
        for entry in entries:
            existing = self._session.scalars(
                select(MxTaxCatalogEntryModel).where(
                    MxTaxCatalogEntryModel.catalog_name == entry["catalog_name"],
                    MxTaxCatalogEntryModel.code == entry["code"],
                    MxTaxCatalogEntryModel.catalog_version == entry["catalog_version"],
                )
            ).first()
            if existing is not None:
                continue
            self._session.add(
                MxTaxCatalogEntryModel(
                    id=uuid4(),
                    catalog_name=entry["catalog_name"],
                    catalog_version=entry["catalog_version"],
                    code=entry["code"],
                    name=entry["name"],
                    person_type=entry.get("person_type"),
                    rate=Decimal(str(entry["rate"])) if entry.get("rate") is not None else None,
                    metadata_json=entry.get("metadata_json"),
                    valid_from=entry["valid_from"],
                    valid_to=entry.get("valid_to"),
                    is_active=True,
                    source_reference=entry.get("source_reference"),
                    loaded_at=datetime.now(UTC),
                    checksum=entry.get("checksum"),
                )
            )
            count += 1
        self._session.flush()
        return count

    def is_empty(self) -> bool:
        return self._session.scalars(select(MxTaxCatalogEntryModel.id).limit(1)).first() is None

    def _row(self, model: MxTaxCatalogEntryModel) -> dict:
        return {
            "catalog_name": model.catalog_name,
            "catalog_version": model.catalog_version,
            "code": model.code,
            "name": model.name,
            "person_type": model.person_type,
            "rate": str(model.rate) if model.rate is not None else None,
            "valid_from": model.valid_from.isoformat(),
            "valid_to": model.valid_to.isoformat() if model.valid_to else None,
        }
