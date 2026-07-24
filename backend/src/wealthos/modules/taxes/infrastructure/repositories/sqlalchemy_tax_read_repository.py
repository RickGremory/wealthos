"""SQLAlchemy TaxReadRepository."""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from wealthos.modules.accounts.infrastructure.models.account_model import AccountModel
from wealthos.modules.taxes.application.services.tax_calculation_service import (
    TaxPaymentView,
    TaxTransactionView,
)
from wealthos.modules.taxes.infrastructure.models.tax_models import TaxPaymentModel
from wealthos.modules.transactions.infrastructure.models.transaction_model import (
    TransactionEntryModel,
    TransactionModel,
)

_UTC = ZoneInfo("UTC")


class SqlAlchemyTaxReadRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_taxable_transactions(
        self,
        organization_id: UUID,
        *,
        date_from: date,
        date_to: date,
    ) -> list[TaxTransactionView]:
        start = datetime.combine(date_from, time.min, tzinfo=_UTC)
        end = datetime.combine(date_to, time.max, tzinfo=_UTC)

        payment_tx_ids = {
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
                func.coalesce(func.max(func.abs(TransactionEntryModel.amount)), 0).label("amount"),
                TransactionEntryModel.currency,
            )
            .join(
                TransactionEntryModel,
                TransactionEntryModel.transaction_id == TransactionModel.id,
            )
            .where(
                TransactionModel.organization_id == organization_id,
                TransactionModel.status == "posted",
                TransactionModel.transaction_type.notin_(("transfer", "adjustment")),
                TransactionModel.occurred_at >= start,
                TransactionModel.occurred_at <= end,
            )
            .group_by(
                TransactionModel.id,
                TransactionModel.transaction_type,
                TransactionModel.status,
                TransactionModel.occurred_at,
                TransactionModel.category_id,
                TransactionEntryModel.currency,
            )
            .order_by(TransactionModel.occurred_at.asc())
        )
        rows = self._session.execute(stmt).all()
        linked_ids = payment_tx_ids

        results: list[TaxTransactionView] = []
        for tx_id, tx_type, status, occurred_at, category_id, amount, currency in rows:
            results.append(
                TaxTransactionView(
                    transaction_id=tx_id,
                    transaction_type=tx_type,
                    status=status,
                    occurred_on=occurred_at.date(),
                    amount=Decimal(str(amount)),
                    currency=str(currency),
                    category_id=category_id,
                    linked_tax_payment=tx_id in linked_ids,
                )
            )
        return results

    def get_period_payments(
        self,
        organization_id: UUID,
        tax_period_id: UUID,
    ) -> list[TaxPaymentView]:
        stmt = select(
            TaxPaymentModel.amount,
            TaxPaymentModel.currency,
            TaxPaymentModel.tax_type,
        ).where(
            TaxPaymentModel.organization_id == organization_id,
            TaxPaymentModel.tax_period_id == tax_period_id,
        )
        return [
            TaxPaymentView(
                amount=Decimal(str(amount)),
                currency=str(currency),
                tax_type=str(tax_type),
            )
            for amount, currency, tax_type in self._session.execute(stmt).all()
        ]

    def get_reserve_account_balance(
        self,
        organization_id: UUID,
        account_id: UUID,
    ) -> Decimal | None:
        stmt = select(AccountModel.current_balance).where(
            AccountModel.organization_id == organization_id,
            AccountModel.id == account_id,
            AccountModel.is_active.is_(True),
        )
        balance = self._session.scalar(stmt)
        if balance is None:
            return None
        return Decimal(str(balance))
