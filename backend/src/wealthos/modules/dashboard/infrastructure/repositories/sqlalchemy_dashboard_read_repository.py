"""SQLAlchemy read model for dashboard aggregations."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from wealthos.modules.accounts.infrastructure.models.account_model import AccountModel
from wealthos.modules.categories.infrastructure.models.category_model import CategoryModel
from wealthos.modules.dashboard.application.value_objects.date_range import DateRange
from wealthos.modules.dashboard.application.views.account_balance import (
    AccountBalanceGroupView,
    AccountBalanceView,
)
from wealthos.modules.dashboard.application.views.cash_flow import (
    CashFlowPointView,
    CashFlowSeriesView,
)
from wealthos.modules.dashboard.application.views.category_spending import (
    CategorySpendingItemView,
    CategorySpendingSeriesView,
)
from wealthos.modules.dashboard.application.views.recent_transaction import (
    NamedRefView,
    RecentTransactionView,
)
from wealthos.modules.dashboard.application.views.summary import (
    CurrencyBalanceView,
    CurrencyCashFlowView,
    DashboardSummaryView,
)
from wealthos.modules.dashboard.domain.value_objects.cash_flow_granularity import (
    CashFlowGranularity,
)
from wealthos.modules.dashboard.domain.value_objects.category_grouping import (
    CategoryGrouping,
)
from wealthos.modules.transactions.infrastructure.models.transaction_model import (
    TransactionEntryModel,
    TransactionModel,
)

_ZERO = Decimal("0.00")
_HUNDRED = Decimal("100")


class SqlAlchemyDashboardReadRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_summary(
        self,
        organization_id: UUID,
        period: DateRange,
        *,
        primary_currency: str,
    ) -> DashboardSummaryView:
        balances = self._currency_balances(organization_id, primary_currency)
        cash_flow = self._period_cash_flow(organization_id, period, primary_currency)
        active, archived = self._account_counts(organization_id)
        tx_count = self._transaction_count(organization_id, period)
        return DashboardSummaryView(
            balances=balances,
            cash_flow=cash_flow,
            active_account_count=active,
            archived_account_count=archived,
            transaction_count=tx_count,
        )

    def get_cash_flow(
        self,
        organization_id: UUID,
        period: DateRange,
        granularity: CashFlowGranularity,
        *,
        primary_currency: str,
    ) -> list[CashFlowSeriesView]:
        trunc_unit = granularity.value
        local_bucket = func.date_trunc(
            trunc_unit,
            func.timezone(period.timezone, TransactionModel.occurred_at),
        )
        stmt = (
            select(
                TransactionEntryModel.currency,
                local_bucket.label("bucket"),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                TransactionModel.transaction_type == "income",
                                TransactionEntryModel.amount,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("income"),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                TransactionModel.transaction_type == "expense",
                                func.abs(TransactionEntryModel.amount),
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("expenses"),
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
                TransactionModel.occurred_at >= period.start,
                TransactionModel.occurred_at < period.end_exclusive,
            )
            .group_by(TransactionEntryModel.currency, local_bucket)
            .order_by(TransactionEntryModel.currency, local_bucket)
        )
        rows = self._session.execute(stmt).all()
        by_currency: dict[str, dict[date, tuple[Decimal, Decimal]]] = defaultdict(dict)
        for currency, bucket, income, expenses in rows:
            bucket_date = bucket.date() if hasattr(bucket, "date") else bucket
            by_currency[str(currency)][bucket_date] = (
                _money(income),
                _money(expenses),
            )

        currencies = self._ordered_currencies(
            set(by_currency.keys()) | self._account_currencies(organization_id),
            primary_currency,
        )
        series: list[CashFlowSeriesView] = []
        buckets = _iter_period_starts(
            period.display_from,
            period.display_to,
            granularity.value,
        )
        for currency in currencies:
            points = []
            data = by_currency.get(currency, {})
            for bucket_start in buckets:
                income, expenses = data.get(bucket_start, (_ZERO, _ZERO))
                points.append(
                    CashFlowPointView(
                        period_start=bucket_start,
                        income=income,
                        expenses=expenses,
                        net_cash_flow=_money(income - expenses),
                    )
                )
            series.append(CashFlowSeriesView(currency=currency, items=tuple(points)))
        return series

    def get_spending_by_category(
        self,
        organization_id: UUID,
        period: DateRange,
        *,
        limit: int,
        group_by: CategoryGrouping,
        primary_currency: str,
    ) -> list[CategorySpendingSeriesView]:
        stmt = (
            select(
                TransactionEntryModel.currency,
                CategoryModel.id.label("category_id"),
                CategoryModel.name.label("category_name"),
                CategoryModel.parent_id.label("parent_id"),
                func.coalesce(
                    func.sum(func.abs(TransactionEntryModel.amount)),
                    0,
                ).label("amount"),
                func.count(func.distinct(TransactionModel.id)).label("tx_count"),
            )
            .select_from(TransactionModel)
            .join(
                TransactionEntryModel,
                TransactionEntryModel.transaction_id == TransactionModel.id,
            )
            .join(CategoryModel, CategoryModel.id == TransactionModel.category_id)
            .where(
                TransactionModel.organization_id == organization_id,
                TransactionModel.status == "posted",
                TransactionModel.transaction_type == "expense",
                TransactionModel.occurred_at >= period.start,
                TransactionModel.occurred_at < period.end_exclusive,
            )
            .group_by(
                TransactionEntryModel.currency,
                CategoryModel.id,
                CategoryModel.name,
                CategoryModel.parent_id,
            )
        )
        rows = self._session.execute(stmt).all()

        parent_ids = {row.parent_id for row in rows if row.parent_id is not None}
        parents: dict[UUID, CategoryModel] = {}
        if parent_ids:
            parents = {
                category.id: category
                for category in self._session.scalars(
                    select(CategoryModel).where(CategoryModel.id.in_(parent_ids))
                ).all()
            }

        by_currency: dict[str, dict[UUID, list]] = defaultdict(
            lambda: defaultdict(lambda: [_ZERO, 0, ""])
        )
        for currency, category_id, category_name, parent_id, amount, tx_count in rows:
            money = _money(amount)
            if group_by.is_root and parent_id is not None:
                group_key = parent_id
                group_name = parents[parent_id].name if parent_id in parents else category_name
            else:
                group_key = category_id
                group_name = category_name
            bucket = by_currency[str(currency)][group_key]
            bucket[0] = _money(bucket[0] + money)
            bucket[1] = int(bucket[1]) + int(tx_count)
            bucket[2] = group_name

        series: list[CategorySpendingSeriesView] = []
        for currency in self._ordered_currencies(set(by_currency.keys()), primary_currency):
            groups = by_currency[currency]
            total = _money(sum((values[0] for values in groups.values()), _ZERO))
            items_raw = sorted(
                (
                    (category_id, values[2], values[0], values[1])
                    for category_id, values in groups.items()
                ),
                key=lambda row: row[2],
                reverse=True,
            )[:limit]
            items = []
            for category_id, category_name, amount, tx_count in items_raw:
                percentage = (
                    _ZERO
                    if total == _ZERO
                    else (amount * _HUNDRED / total).quantize(
                        Decimal("0.01"),
                        rounding=ROUND_HALF_UP,
                    )
                )
                items.append(
                    CategorySpendingItemView(
                        category_id=category_id,
                        category_name=category_name,
                        amount=amount,
                        percentage=percentage,
                        transaction_count=tx_count,
                    )
                )
            series.append(
                CategorySpendingSeriesView(
                    currency=currency,
                    total_expenses=total,
                    items=tuple(items),
                )
            )
        return series

    def get_account_balances(
        self,
        organization_id: UUID,
        *,
        include_archived: bool = False,
        primary_currency: str,
    ) -> list[AccountBalanceGroupView]:
        stmt = select(AccountModel).where(AccountModel.organization_id == organization_id)
        if not include_archived:
            stmt = stmt.where(AccountModel.is_active.is_(True))
        stmt = stmt.order_by(
            AccountModel.currency.asc(),
            case((AccountModel.classification == "asset", 0), else_=1),
            AccountModel.account_type.asc(),
            AccountModel.name.asc(),
        )
        models = self._session.scalars(stmt).all()
        by_currency: dict[str, list[AccountBalanceView]] = defaultdict(list)
        for model in models:
            balance = _money(model.current_balance)
            display = abs(balance) if model.classification == "liability" else balance
            by_currency[model.currency].append(
                AccountBalanceView(
                    account_id=model.id,
                    name=model.name,
                    account_type=model.account_type,
                    classification=model.classification,
                    currency=model.currency,
                    institution_name=model.institution_name,
                    current_balance=balance,
                    display_balance=display,
                    is_active=model.is_active,
                )
            )
        return [
            AccountBalanceGroupView(currency=currency, accounts=tuple(by_currency[currency]))
            for currency in self._ordered_currencies(set(by_currency.keys()), primary_currency)
        ]

    def get_recent_transactions(
        self,
        organization_id: UUID,
        *,
        limit: int,
    ) -> list[RecentTransactionView]:
        stmt = (
            select(TransactionModel)
            .where(TransactionModel.organization_id == organization_id)
            .order_by(
                TransactionModel.occurred_at.desc(),
                TransactionModel.created_at.desc(),
            )
            .limit(limit)
        )
        transactions = list(self._session.scalars(stmt).unique().all())
        if not transactions:
            return []

        # Eager load entries via separate query to avoid N+1 identity map issues.
        tx_ids = [tx.id for tx in transactions]
        entries = self._session.scalars(
            select(TransactionEntryModel).where(TransactionEntryModel.transaction_id.in_(tx_ids))
        ).all()
        entries_by_tx: dict[UUID, list[TransactionEntryModel]] = defaultdict(list)
        account_ids: set[UUID] = set()
        for entry in entries:
            entries_by_tx[entry.transaction_id].append(entry)
            account_ids.add(entry.account_id)

        category_ids = {tx.category_id for tx in transactions if tx.category_id}
        accounts: dict[UUID, AccountModel] = {}
        if account_ids:
            accounts = {
                account.id: account
                for account in self._session.scalars(
                    select(AccountModel).where(AccountModel.id.in_(account_ids))
                ).all()
            }
        categories: dict[UUID, CategoryModel] = {}
        if category_ids:
            categories = {
                category.id: category
                for category in self._session.scalars(
                    select(CategoryModel).where(CategoryModel.id.in_(category_ids))
                ).all()
            }

        # Preserve order from transactions query.
        results: list[RecentTransactionView] = []
        for tx in transactions:
            tx_entries = entries_by_tx.get(tx.id, [])
            category = None
            if tx.category_id and tx.category_id in categories:
                cat = categories[tx.category_id]
                category = NamedRefView(id=cat.id, name=cat.name)

            account_ref = None
            source = None
            destination = None
            amount = _ZERO
            currency = "MXN"

            if tx.transaction_type == "transfer" and len(tx_entries) == 2:
                debit = next(e for e in tx_entries if e.amount < 0)
                credit = next(e for e in tx_entries if e.amount > 0)
                amount = _money(abs(debit.amount))
                currency = debit.currency
                if debit.account_id in accounts:
                    src = accounts[debit.account_id]
                    source = NamedRefView(id=src.id, name=src.name)
                if credit.account_id in accounts:
                    dst = accounts[credit.account_id]
                    destination = NamedRefView(id=dst.id, name=dst.name)
            elif tx_entries:
                entry = tx_entries[0]
                amount = _money(abs(entry.amount))
                currency = entry.currency
                if entry.account_id in accounts:
                    acc = accounts[entry.account_id]
                    account_ref = NamedRefView(id=acc.id, name=acc.name)

            results.append(
                RecentTransactionView(
                    id=tx.id,
                    transaction_type=tx.transaction_type,
                    description=tx.description,
                    category=category,
                    occurred_at=tx.occurred_at,
                    status=tx.status,
                    amount=amount,
                    currency=currency,
                    account=account_ref,
                    source_account=source,
                    destination_account=destination,
                )
            )
        return results

    def _currency_balances(
        self,
        organization_id: UUID,
        primary_currency: str,
    ) -> tuple[CurrencyBalanceView, ...]:
        stmt = (
            select(
                AccountModel.currency,
                func.coalesce(
                    func.sum(
                        case(
                            (
                                AccountModel.classification == "asset",
                                AccountModel.current_balance,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("assets"),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                AccountModel.classification == "liability",
                                func.abs(AccountModel.current_balance),
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("liabilities"),
            )
            .where(
                AccountModel.organization_id == organization_id,
                AccountModel.is_active.is_(True),
            )
            .group_by(AccountModel.currency)
        )
        rows = {
            str(currency): (_money(assets), _money(liabilities))
            for currency, assets, liabilities in self._session.execute(stmt).all()
        }
        currencies = self._ordered_currencies(set(rows.keys()), primary_currency)
        if not currencies and primary_currency:
            currencies = [primary_currency]
            rows[primary_currency] = (_ZERO, _ZERO)
        return tuple(
            CurrencyBalanceView(
                currency=currency,
                total_assets=rows.get(currency, (_ZERO, _ZERO))[0],
                total_liabilities=rows.get(currency, (_ZERO, _ZERO))[1],
                net_worth=_money(
                    rows.get(currency, (_ZERO, _ZERO))[0] - rows.get(currency, (_ZERO, _ZERO))[1]
                ),
            )
            for currency in currencies
        )

    def _period_cash_flow(
        self,
        organization_id: UUID,
        period: DateRange,
        primary_currency: str,
    ) -> tuple[CurrencyCashFlowView, ...]:
        stmt = (
            select(
                TransactionEntryModel.currency,
                func.coalesce(
                    func.sum(
                        case(
                            (
                                TransactionModel.transaction_type == "income",
                                TransactionEntryModel.amount,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("income"),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                TransactionModel.transaction_type == "expense",
                                func.abs(TransactionEntryModel.amount),
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("expenses"),
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
                TransactionModel.occurred_at >= period.start,
                TransactionModel.occurred_at < period.end_exclusive,
            )
            .group_by(TransactionEntryModel.currency)
        )
        rows = {
            str(currency): (_money(income), _money(expenses))
            for currency, income, expenses in self._session.execute(stmt).all()
        }
        currencies = self._ordered_currencies(set(rows.keys()), primary_currency)
        if not currencies:
            currencies = [primary_currency]
            rows[primary_currency] = (_ZERO, _ZERO)
        return tuple(
            CurrencyCashFlowView(
                currency=currency,
                income=rows.get(currency, (_ZERO, _ZERO))[0],
                expenses=rows.get(currency, (_ZERO, _ZERO))[1],
                net_cash_flow=_money(
                    rows.get(currency, (_ZERO, _ZERO))[0] - rows.get(currency, (_ZERO, _ZERO))[1]
                ),
            )
            for currency in currencies
        )

    def _account_counts(self, organization_id: UUID) -> tuple[int, int]:
        stmt = select(
            func.coalesce(
                func.sum(case((AccountModel.is_active.is_(True), 1), else_=0)),
                0,
            ),
            func.coalesce(
                func.sum(case((AccountModel.is_active.is_(False), 1), else_=0)),
                0,
            ),
        ).where(AccountModel.organization_id == organization_id)
        active, archived = self._session.execute(stmt).one()
        return int(active or 0), int(archived or 0)

    def _transaction_count(self, organization_id: UUID, period: DateRange) -> int:
        stmt = (
            select(func.count())
            .select_from(TransactionModel)
            .where(
                TransactionModel.organization_id == organization_id,
                TransactionModel.occurred_at >= period.start,
                TransactionModel.occurred_at < period.end_exclusive,
            )
        )
        return int(self._session.scalar(stmt) or 0)

    def _account_currencies(self, organization_id: UUID) -> set[str]:
        stmt = (
            select(AccountModel.currency)
            .where(
                AccountModel.organization_id == organization_id,
                AccountModel.is_active.is_(True),
            )
            .distinct()
        )
        return {str(row[0]) for row in self._session.execute(stmt).all()}

    def _ordered_currencies(
        self,
        currencies: set[str],
        primary_currency: str,
    ) -> list[str]:
        ordered = []
        if primary_currency in currencies:
            ordered.append(primary_currency)
        ordered.extend(sorted(c for c in currencies if c != primary_currency))
        return ordered


def _money(value: Decimal | int | float | str | None) -> Decimal:
    if value is None:
        return _ZERO
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _iter_period_starts(start: date, end: date, granularity: str) -> list[date]:
    points: list[date] = []
    current = start
    if granularity == "day":
        while current <= end:
            points.append(current)
            current += timedelta(days=1)
        return points
    if granularity == "week":
        # Align to Monday of the week containing start.
        current = start - timedelta(days=start.weekday())
        while current <= end:
            points.append(current)
            current += timedelta(days=7)
        return points
    # month
    current = date(start.year, start.month, 1)
    while current <= end:
        points.append(current)
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return points
