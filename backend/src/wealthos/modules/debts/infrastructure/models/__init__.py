"""ORM models package for debts."""

from wealthos.modules.debts.infrastructure.models.debt_model import (
    DebtModel,
    DebtPaymentModel,
)

__all__ = ["DebtModel", "DebtPaymentModel"]
