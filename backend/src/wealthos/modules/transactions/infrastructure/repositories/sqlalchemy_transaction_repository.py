"""SQLAlchemy implementation of TransactionRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from wealthos.modules.transactions.domain.entities.transaction import Transaction
from wealthos.modules.transactions.domain.repositories.transaction_repository import (
    TransactionFilters,
    TransactionListResult,
)
from wealthos.modules.transactions.infrastructure.mappers.transaction_mapper import (
    TransactionMapper,
)
from wealthos.modules.transactions.infrastructure.models.transaction_model import (
    TransactionEntryModel,
    TransactionModel,
)
from wealthos.shared.base import BaseRepository


class SqlAlchemyTransactionRepository(BaseRepository[TransactionModel]):
    def __init__(self, session: Session, mapper: TransactionMapper | None = None) -> None:
        super().__init__(session, TransactionModel)
        self._mapper = mapper or TransactionMapper()

    def add(self, transaction: Transaction) -> Transaction:
        model = self._mapper.to_model(transaction)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get_by_id(
        self,
        organization_id: UUID,
        transaction_id: UUID,
    ) -> Transaction | None:
        stmt = (
            select(TransactionModel)
            .options(selectinload(TransactionModel.entries))
            .where(
                TransactionModel.organization_id == organization_id,
                TransactionModel.id == transaction_id,
            )
        )
        model = self.session.scalars(stmt).first()
        if model is None:
            return None
        return self._mapper.to_entity(model)

    def list_by_organization(
        self,
        organization_id: UUID,
        filters: TransactionFilters,
    ) -> TransactionListResult:
        base = select(TransactionModel).where(
            TransactionModel.organization_id == organization_id,
        )
        base = self._apply_filters(base, filters)

        count_stmt = select(func.count()).select_from(base.subquery())
        total = int(self.session.scalar(count_stmt) or 0)

        stmt = (
            base.options(selectinload(TransactionModel.entries))
            .order_by(
                TransactionModel.occurred_at.desc(),
                TransactionModel.created_at.desc(),
            )
            .limit(filters.limit)
            .offset(filters.offset)
        )
        models = self.session.scalars(stmt).unique().all()
        return TransactionListResult(
            items=[self._mapper.to_entity(model) for model in models],
            total=total,
        )

    def save(self, transaction: Transaction) -> Transaction:
        model = self.session.get(
            TransactionModel,
            transaction.id,
            options=(selectinload(TransactionModel.entries),),
        )
        if model is None or model.organization_id != transaction.organization_id:
            raise LookupError("Transaction not found for save.")
        self._mapper.apply_to_model(transaction, model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def _apply_filters(self, stmt, filters: TransactionFilters):  # noqa: ANN001
        if filters.transaction_type is not None:
            stmt = stmt.where(TransactionModel.transaction_type == filters.transaction_type)
        if filters.status is not None:
            stmt = stmt.where(TransactionModel.status == filters.status)
        if filters.category_id is not None:
            stmt = stmt.where(TransactionModel.category_id == filters.category_id)
        if filters.date_from is not None:
            stmt = stmt.where(TransactionModel.occurred_at >= filters.date_from)
        if filters.date_to is not None:
            stmt = stmt.where(TransactionModel.occurred_at <= filters.date_to)
        if filters.search:
            pattern = f"%{filters.search.strip()}%"
            stmt = stmt.where(
                or_(
                    TransactionModel.description.ilike(pattern),
                    TransactionModel.notes.ilike(pattern),
                )
            )
        if (
            filters.account_id is not None
            or filters.min_amount is not None
            or filters.max_amount is not None
        ):
            entry_exists = select(TransactionEntryModel.id).where(
                TransactionEntryModel.transaction_id == TransactionModel.id
            )
            if filters.account_id is not None:
                entry_exists = entry_exists.where(
                    TransactionEntryModel.account_id == filters.account_id
                )
            if filters.min_amount is not None:
                entry_exists = entry_exists.where(
                    func.abs(TransactionEntryModel.amount) >= filters.min_amount
                )
            if filters.max_amount is not None:
                entry_exists = entry_exists.where(
                    func.abs(TransactionEntryModel.amount) <= filters.max_amount
                )
            stmt = stmt.where(entry_exists.exists())
        return stmt
