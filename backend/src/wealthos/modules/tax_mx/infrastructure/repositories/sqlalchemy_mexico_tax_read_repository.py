"""SQLAlchemy MexicoTaxReadRepository."""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from wealthos.modules.tax_mx.application.services.mexico_tax_calculation_service import (
    MexicoTaxTransactionView,
)
from wealthos.modules.tax_mx.infrastructure.models.tax_mx_models import (
    MexicoTaxCategoryMappingModel,
    MexicoTaxTransactionOverrideModel,
    TaxEvidenceModel,
)
from wealthos.modules.taxes.infrastructure.models.tax_models import TaxPaymentModel
from wealthos.modules.transactions.infrastructure.models.transaction_model import (
    TransactionEntryModel,
    TransactionModel,
)

_UTC = ZoneInfo("UTC")


class SqlAlchemyMexicoTaxReadRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_period_transactions(
        self,
        organization_id: UUID,
        *,
        date_from: date,
        date_to: date,
        currency: str | None = None,
    ) -> list[MexicoTaxTransactionView]:
        start = datetime.combine(date_from, time.min, tzinfo=_UTC)
        end = datetime.combine(date_to, time.max, tzinfo=_UTC)
        payment_ids = {
            row[0]
            for row in self._session.execute(
                select(TaxPaymentModel.transaction_id).where(
                    TaxPaymentModel.organization_id == organization_id
                )
            ).all()
        }
        stmt = (
            select(
                TransactionModel.id,
                TransactionModel.transaction_type,
                TransactionModel.status,
                TransactionModel.occurred_at,
                TransactionModel.category_id,
                TransactionModel.description,
                TransactionModel.updated_at,
                func.coalesce(func.max(func.abs(TransactionEntryModel.amount)), 0),
                TransactionEntryModel.currency,
            )
            .join(
                TransactionEntryModel,
                TransactionEntryModel.transaction_id == TransactionModel.id,
            )
            .where(
                TransactionModel.organization_id == organization_id,
                TransactionModel.status == "posted",
                TransactionModel.occurred_at >= start,
                TransactionModel.occurred_at <= end,
            )
            .group_by(
                TransactionModel.id,
                TransactionModel.transaction_type,
                TransactionModel.status,
                TransactionModel.occurred_at,
                TransactionModel.category_id,
                TransactionModel.description,
                TransactionModel.updated_at,
                TransactionEntryModel.currency,
            )
            .order_by(TransactionModel.occurred_at.asc())
        )
        if currency is not None:
            stmt = stmt.where(TransactionEntryModel.currency == currency)
        rows = self._session.execute(stmt).all()
        return [
            MexicoTaxTransactionView(
                transaction_id=tx_id,
                transaction_type=tx_type,
                status=status,
                occurred_on=occurred_at.date(),
                amount=Decimal(str(amount)),
                currency=str(curr),
                category_id=category_id,
                description=description or "",
                updated_at=updated_at.date() if updated_at else None,
                linked_tax_payment=tx_id in payment_ids,
            )
            for (
                tx_id,
                tx_type,
                status,
                occurred_at,
                category_id,
                description,
                updated_at,
                amount,
                curr,
            ) in rows
        ]

    def get_unclassified_transactions(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        transaction_type: str | None = None,
        category_id: UUID | None = None,
        account_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[MexicoTaxTransactionView], int]:
        mapped_categories = select(MexicoTaxCategoryMappingModel.category_id).where(
            MexicoTaxCategoryMappingModel.organization_id == organization_id,
            MexicoTaxCategoryMappingModel.tax_profile_id == tax_profile_id,
        )
        overridden = select(MexicoTaxTransactionOverrideModel.transaction_id).where(
            MexicoTaxTransactionOverrideModel.organization_id == organization_id,
            MexicoTaxTransactionOverrideModel.tax_profile_id == tax_profile_id,
        )
        stmt = (
            select(
                TransactionModel.id,
                TransactionModel.transaction_type,
                TransactionModel.status,
                TransactionModel.occurred_at,
                TransactionModel.category_id,
                TransactionModel.description,
                TransactionModel.updated_at,
                func.coalesce(func.max(func.abs(TransactionEntryModel.amount)), 0),
                TransactionEntryModel.currency,
            )
            .join(
                TransactionEntryModel,
                TransactionEntryModel.transaction_id == TransactionModel.id,
            )
            .where(
                TransactionModel.organization_id == organization_id,
                TransactionModel.status == "posted",
                TransactionModel.transaction_type.in_(("income", "expense")),
                TransactionModel.id.notin_(overridden),
                (
                    TransactionModel.category_id.is_(None)
                    | TransactionModel.category_id.notin_(mapped_categories)
                ),
            )
            .group_by(
                TransactionModel.id,
                TransactionModel.transaction_type,
                TransactionModel.status,
                TransactionModel.occurred_at,
                TransactionModel.category_id,
                TransactionModel.description,
                TransactionModel.updated_at,
                TransactionEntryModel.currency,
            )
            .order_by(TransactionModel.occurred_at.desc())
        )
        if date_from is not None:
            stmt = stmt.where(
                TransactionModel.occurred_at >= datetime.combine(date_from, time.min, tzinfo=_UTC)
            )
        if date_to is not None:
            stmt = stmt.where(
                TransactionModel.occurred_at <= datetime.combine(date_to, time.max, tzinfo=_UTC)
            )
        if transaction_type is not None:
            stmt = stmt.where(TransactionModel.transaction_type == transaction_type)
        if category_id is not None:
            stmt = stmt.where(TransactionModel.category_id == category_id)
        if account_id is not None:
            stmt = stmt.where(TransactionEntryModel.account_id == account_id)

        rows = list(self._session.execute(stmt).all())
        total = len(rows)
        page = rows[offset : offset + limit]
        items = [
            MexicoTaxTransactionView(
                transaction_id=tx_id,
                transaction_type=tx_type,
                status=status,
                occurred_on=occurred_at.date(),
                amount=Decimal(str(amount)),
                currency=str(curr),
                category_id=category_id_,
                description=description or "",
                updated_at=updated_at.date() if updated_at else None,
            )
            for (
                tx_id,
                tx_type,
                status,
                occurred_at,
                category_id_,
                description,
                updated_at,
                amount,
                curr,
            ) in page
        ]
        return items, total

    def latest_relevant_change_at(
        self,
        organization_id: UUID,
        *,
        date_from: date,
        date_to: date,
    ) -> datetime | None:
        start = datetime.combine(date_from, time.min, tzinfo=_UTC)
        end = datetime.combine(date_to, time.max, tzinfo=_UTC)
        tx_max = self._session.scalar(
            select(func.max(TransactionModel.updated_at)).where(
                TransactionModel.organization_id == organization_id,
                TransactionModel.occurred_at >= start,
                TransactionModel.occurred_at <= end,
            )
        )
        evidence_max = self._session.scalar(
            select(func.max(TaxEvidenceModel.updated_at)).where(
                TaxEvidenceModel.organization_id == organization_id
            )
        )
        candidates = [value for value in (tx_max, evidence_max) if value is not None]
        return max(candidates) if candidates else None
