"""SQLAlchemy TaxPaymentRepository."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from wealthos.modules.taxes.domain.entities.tax_payment import TaxPayment
from wealthos.modules.taxes.infrastructure.mappers.tax_payment_mapper import TaxPaymentMapper
from wealthos.modules.taxes.infrastructure.models.tax_models import TaxPaymentModel
from wealthos.shared.base import BaseRepository

_ZERO = Decimal("0.00")


class SqlAlchemyTaxPaymentRepository(BaseRepository[TaxPaymentModel]):
    def __init__(self, session: Session, mapper: TaxPaymentMapper | None = None) -> None:
        super().__init__(session, TaxPaymentModel)
        self._mapper = mapper or TaxPaymentMapper()

    def add(self, payment: TaxPayment) -> TaxPayment:
        model = self._mapper.to_model(payment)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get_by_idempotency_key(
        self,
        organization_id: UUID,
        idempotency_key: str,
    ) -> TaxPayment | None:
        stmt = select(TaxPaymentModel).where(
            TaxPaymentModel.organization_id == organization_id,
            TaxPaymentModel.idempotency_key == idempotency_key,
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def list_by_period(
        self,
        organization_id: UUID,
        tax_period_id: UUID,
    ) -> list[TaxPayment]:
        stmt = (
            select(TaxPaymentModel)
            .where(
                TaxPaymentModel.organization_id == organization_id,
                TaxPaymentModel.tax_period_id == tax_period_id,
            )
            .order_by(TaxPaymentModel.paid_at.desc())
        )
        return [self._mapper.to_entity(model) for model in self.session.scalars(stmt)]

    def sum_by_period(
        self,
        organization_id: UUID,
        tax_period_id: UUID,
        *,
        currency: str | None = None,
    ) -> Decimal:
        stmt = select(func.coalesce(func.sum(TaxPaymentModel.amount), 0)).where(
            TaxPaymentModel.organization_id == organization_id,
            TaxPaymentModel.tax_period_id == tax_period_id,
        )
        if currency is not None:
            stmt = stmt.where(TaxPaymentModel.currency == currency)
        total = self.session.scalar(stmt)
        return Decimal(str(total or _ZERO))
