"""SQLAlchemy DebtPaymentRepository."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from wealthos.modules.debts.domain.entities.debt_payment import DebtPayment
from wealthos.modules.debts.infrastructure.mappers.debt_payment_mapper import (
    DebtPaymentMapper,
)
from wealthos.modules.debts.infrastructure.models.debt_model import DebtPaymentModel
from wealthos.shared.base import BaseRepository


class SqlAlchemyDebtPaymentRepository(BaseRepository[DebtPaymentModel]):
    def __init__(
        self,
        session: Session,
        mapper: DebtPaymentMapper | None = None,
    ) -> None:
        super().__init__(session, DebtPaymentModel)
        self._mapper = mapper or DebtPaymentMapper()

    def add(self, payment: DebtPayment) -> DebtPayment:
        model = self._mapper.to_model(payment)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def list_by_debt(
        self,
        organization_id: UUID,
        debt_id: UUID,
        *,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[DebtPayment], int]:
        filters = [
            DebtPaymentModel.organization_id == organization_id,
            DebtPaymentModel.debt_id == debt_id,
        ]
        if date_from is not None:
            filters.append(DebtPaymentModel.paid_at >= date_from)
        if date_to is not None:
            filters.append(DebtPaymentModel.paid_at <= date_to)

        total = self.session.scalar(
            select(func.count()).select_from(DebtPaymentModel).where(*filters)
        )
        stmt = (
            select(DebtPaymentModel)
            .where(*filters)
            .order_by(DebtPaymentModel.paid_at.desc())
            .limit(limit)
            .offset(offset)
        )
        items = [self._mapper.to_entity(model) for model in self.session.scalars(stmt)]
        return items, int(total or 0)
