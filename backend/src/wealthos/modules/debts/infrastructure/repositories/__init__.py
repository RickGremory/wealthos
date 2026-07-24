"""Repositories package for debts."""

from wealthos.modules.debts.infrastructure.repositories.sqlalchemy_debt_payment_repository import (
    SqlAlchemyDebtPaymentRepository,
)
from wealthos.modules.debts.infrastructure.repositories.sqlalchemy_debt_repository import (
    SqlAlchemyDebtRepository,
)

__all__ = ["SqlAlchemyDebtPaymentRepository", "SqlAlchemyDebtRepository"]
