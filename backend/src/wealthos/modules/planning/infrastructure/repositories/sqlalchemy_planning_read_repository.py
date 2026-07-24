"""SQLAlchemy PlanningReadRepository — cross-module planning queries."""

from __future__ import annotations

import calendar
from collections.abc import Sequence
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from wealthos.modules.accounts.infrastructure.models.account_model import AccountModel
from wealthos.modules.categories.infrastructure.models.category_model import CategoryModel
from wealthos.modules.debts.infrastructure.models.debt_model import (
    DebtModel,
    DebtPaymentModel,
)
from wealthos.modules.planning.domain.views import (
    BudgetActualsView,
    CategoryActualView,
    LiquidAccountBalanceView,
    PlanningCommitmentView,
)
from wealthos.modules.taxes.infrastructure.models.tax_models import (
    TaxCalculationModel,
    TaxPaymentModel,
    TaxPeriodModel,
)
from wealthos.modules.transactions.infrastructure.models.transaction_model import (
    TransactionEntryModel,
    TransactionModel,
)
from wealthos.shared.domain.value_objects.currency import Currency

_UTC = ZoneInfo("UTC")
_ZERO = Decimal("0.00")
_LIQUID_TYPES = ("checking", "savings", "cash", "digital_wallet")
_LINKED_PRIORITY = 40


class SqlAlchemyPlanningReadRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_budget_actuals(
        self,
        organization_id: UUID,
        budget_id: UUID,
        *,
        date_from: date,
        date_to: date,
        currency: Currency | str,
    ) -> BudgetActualsView:
        currency_code = _currency_code(currency)
        start, end = _inclusive_range(date_from, date_to)

        # Amount lives on transaction_entries; category/type on transactions.
        # Income entries are positive; expense entries are stored negative — use abs().
        stmt = (
            select(
                TransactionModel.category_id,
                TransactionModel.transaction_type,
                func.coalesce(
                    func.sum(func.abs(TransactionEntryModel.amount)),
                    0,
                ).label("actual_amount"),
            )
            .select_from(TransactionModel)
            .join(
                TransactionEntryModel,
                TransactionEntryModel.transaction_id == TransactionModel.id,
            )
            .where(
                TransactionModel.organization_id == organization_id,
                TransactionModel.status == "posted",
                TransactionModel.transaction_type.in_(("income", "expense")),
                TransactionEntryModel.currency == currency_code,
                TransactionModel.occurred_at >= start,
                TransactionModel.occurred_at <= end,
            )
            .group_by(TransactionModel.category_id, TransactionModel.transaction_type)
            .order_by(TransactionModel.transaction_type, TransactionModel.category_id)
        )
        rows = self._session.execute(stmt).all()

        income_actual = _ZERO
        expense_actual = _ZERO
        by_category: list[CategoryActualView] = []
        for category_id, tx_type, amount in rows:
            value = Decimal(str(amount))
            if tx_type == "income":
                income_actual += value
                allocation_type = "income"
            else:
                expense_actual += value
                allocation_type = "expense"
            by_category.append(
                CategoryActualView(
                    category_id=category_id,
                    allocation_type=allocation_type,
                    actual_amount=value,
                )
            )

        return BudgetActualsView(
            budget_id=budget_id,
            currency=currency_code,
            date_from=date_from,
            date_to=date_to,
            income_actual=income_actual,
            expense_actual=expense_actual,
            by_category=tuple(by_category),
        )

    def get_liquid_account_balances(
        self,
        organization_id: UUID,
        currency: Currency | str,
        account_ids: Sequence[UUID] | None = None,
    ) -> list[LiquidAccountBalanceView]:
        currency_code = _currency_code(currency)
        stmt = select(AccountModel).where(
            AccountModel.organization_id == organization_id,
            AccountModel.currency == currency_code,
            AccountModel.is_active.is_(True),
            AccountModel.account_type.in_(_LIQUID_TYPES),
            AccountModel.archived_at.is_(None),
        )
        if account_ids is not None:
            if not account_ids:
                return []
            stmt = stmt.where(AccountModel.id.in_(tuple(account_ids)))
        stmt = stmt.order_by(AccountModel.name.asc())
        return [
            LiquidAccountBalanceView(
                account_id=model.id,
                account_type=model.account_type,
                currency=model.currency,
                current_balance=Decimal(str(model.current_balance)),
            )
            for model in self._session.scalars(stmt)
        ]

    def get_average_daily_expenses(
        self,
        organization_id: UUID,
        currency: Currency | str,
        lookback_days: int,
    ) -> Decimal:
        if lookback_days <= 0:
            return _ZERO
        currency_code = _currency_code(currency)
        end = datetime.now(_UTC)
        start = end - timedelta(days=lookback_days)
        stmt = (
            select(func.coalesce(func.sum(func.abs(TransactionEntryModel.amount)), 0))
            .select_from(TransactionModel)
            .join(
                TransactionEntryModel,
                TransactionEntryModel.transaction_id == TransactionModel.id,
            )
            .where(
                TransactionModel.organization_id == organization_id,
                TransactionModel.status == "posted",
                TransactionModel.transaction_type == "expense",
                TransactionEntryModel.currency == currency_code,
                TransactionModel.occurred_at >= start,
                TransactionModel.occurred_at <= end,
            )
        )
        total = Decimal(str(self._session.scalar(stmt) or 0))
        return total / Decimal(lookback_days)

    def get_linked_commitments(
        self,
        organization_id: UUID,
        *,
        date_from: date,
        date_to: date,
        currency: Currency | str,
    ) -> list[PlanningCommitmentView]:
        currency_code = _currency_code(currency)
        commitments: list[PlanningCommitmentView] = []
        commitments.extend(
            self._debt_commitments(organization_id, date_from, date_to, currency_code)
        )
        commitments.extend(
            self._tax_commitments(organization_id, date_from, date_to, currency_code)
        )
        commitments.sort(key=lambda c: (c.expected_date, c.priority, c.description))
        return commitments

    def get_debt_payment_actuals(
        self,
        organization_id: UUID,
        debt_id: UUID,
        *,
        date_from: date,
        date_to: date,
    ) -> Decimal:
        start, end = _inclusive_range(date_from, date_to)
        stmt = select(func.coalesce(func.sum(DebtPaymentModel.amount), 0)).where(
            DebtPaymentModel.organization_id == organization_id,
            DebtPaymentModel.debt_id == debt_id,
            DebtPaymentModel.paid_at >= start,
            DebtPaymentModel.paid_at <= end,
        )
        return Decimal(str(self._session.scalar(stmt) or 0))

    def get_tax_payment_actuals(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
        *,
        date_from: date,
        date_to: date,
    ) -> Decimal:
        start, end = _inclusive_range(date_from, date_to)
        stmt = (
            select(func.coalesce(func.sum(TaxPaymentModel.amount), 0))
            .select_from(TaxPaymentModel)
            .join(TaxPeriodModel, TaxPeriodModel.id == TaxPaymentModel.tax_period_id)
            .where(
                TaxPaymentModel.organization_id == organization_id,
                TaxPeriodModel.tax_profile_id == tax_profile_id,
                TaxPaymentModel.paid_at >= start,
                TaxPaymentModel.paid_at <= end,
            )
        )
        return Decimal(str(self._session.scalar(stmt) or 0))

    def get_category_type(
        self,
        organization_id: UUID,
        category_id: UUID,
    ) -> str | None:
        stmt = select(CategoryModel.category_type).where(
            CategoryModel.organization_id == organization_id,
            CategoryModel.id == category_id,
        )
        return self._session.scalar(stmt)

    def _debt_commitments(
        self,
        organization_id: UUID,
        date_from: date,
        date_to: date,
        currency: str,
    ) -> list[PlanningCommitmentView]:
        stmt = select(DebtModel).where(
            DebtModel.organization_id == organization_id,
            DebtModel.currency == currency,
            DebtModel.status == "active",
            DebtModel.archived_at.is_(None),
            DebtModel.minimum_payment > 0,
        )
        results: list[PlanningCommitmentView] = []
        for debt in self._session.scalars(stmt):
            for expected in _payment_dates_in_range(
                date_from,
                date_to,
                debt.payment_day,
            ):
                results.append(
                    PlanningCommitmentView(
                        source="linked_module_recommendation",
                        source_id=debt.id,
                        description=f"Minimum payment — {debt.name}",
                        expected_date=expected,
                        amount=Decimal(str(debt.minimum_payment)),
                        currency=debt.currency,
                        linked_entity_type="debt",
                        linked_entity_id=debt.id,
                        priority=_LINKED_PRIORITY,
                    )
                )
        return results

    def _tax_commitments(
        self,
        organization_id: UUID,
        date_from: date,
        date_to: date,
        currency: str,
    ) -> list[PlanningCommitmentView]:
        periods = self._session.scalars(
            select(TaxPeriodModel).where(
                TaxPeriodModel.organization_id == organization_id,
                TaxPeriodModel.currency == currency,
                TaxPeriodModel.status.in_(("open", "calculated")),
                TaxPeriodModel.date_to >= date_from,
                TaxPeriodModel.date_from <= date_to,
            )
        ).all()
        if not periods:
            return []

        period_ids = [p.id for p in periods]
        latest_calc = (
            select(
                TaxCalculationModel.tax_period_id,
                TaxCalculationModel.estimated_tax,
                func.row_number()
                .over(
                    partition_by=TaxCalculationModel.tax_period_id,
                    order_by=TaxCalculationModel.version.desc(),
                )
                .label("rn"),
            )
            .where(
                TaxCalculationModel.organization_id == organization_id,
                TaxCalculationModel.tax_period_id.in_(period_ids),
                TaxCalculationModel.status == "completed",
            )
            .subquery()
        )
        estimated_rows = {
            row.tax_period_id: Decimal(str(row.estimated_tax))
            for row in self._session.execute(
                select(latest_calc.c.tax_period_id, latest_calc.c.estimated_tax).where(
                    latest_calc.c.rn == 1
                )
            ).all()
        }
        paid_rows = {
            row.tax_period_id: Decimal(str(row.paid))
            for row in self._session.execute(
                select(
                    TaxPaymentModel.tax_period_id,
                    func.coalesce(func.sum(TaxPaymentModel.amount), 0).label("paid"),
                )
                .where(
                    TaxPaymentModel.organization_id == organization_id,
                    TaxPaymentModel.tax_period_id.in_(period_ids),
                )
                .group_by(TaxPaymentModel.tax_period_id)
            ).all()
        }

        results: list[PlanningCommitmentView] = []
        for period in periods:
            estimated = estimated_rows.get(period.id, _ZERO)
            paid = paid_rows.get(period.id, _ZERO)
            balance = estimated - paid
            if balance <= _ZERO:
                continue
            expected = period.date_to
            if expected < date_from or expected > date_to:
                # Due date outside window but period overlaps — pin to range edge.
                expected = min(max(expected, date_from), date_to)
            results.append(
                PlanningCommitmentView(
                    source="linked_module_recommendation",
                    source_id=period.id,
                    description=f"Tax balance due — {period.period_type}",
                    expected_date=expected,
                    amount=balance,
                    currency=period.currency,
                    linked_entity_type="tax_period",
                    linked_entity_id=period.id,
                    priority=_LINKED_PRIORITY,
                )
            )
        return results


def _currency_code(currency: Currency | str) -> str:
    return currency.value if isinstance(currency, Currency) else str(currency).upper()


def _inclusive_range(date_from: date, date_to: date) -> tuple[datetime, datetime]:
    start = datetime.combine(date_from, time.min, tzinfo=_UTC)
    end = datetime.combine(date_to, time.max, tzinfo=_UTC)
    return start, end


def _payment_dates_in_range(
    date_from: date,
    date_to: date,
    payment_day: int | None,
) -> list[date]:
    if payment_day is None:
        return [date_from]
    day = max(1, min(int(payment_day), 31))
    dates: list[date] = []
    cursor = date(date_from.year, date_from.month, 1)
    end_month = date(date_to.year, date_to.month, 1)
    while cursor <= end_month:
        last_day = calendar.monthrange(cursor.year, cursor.month)[1]
        candidate = date(cursor.year, cursor.month, min(day, last_day))
        if date_from <= candidate <= date_to:
            dates.append(candidate)
        if cursor.month == 12:
            cursor = date(cursor.year + 1, 1, 1)
        else:
            cursor = date(cursor.year, cursor.month + 1, 1)
    return dates
