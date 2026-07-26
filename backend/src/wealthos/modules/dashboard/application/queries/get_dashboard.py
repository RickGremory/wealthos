"""GetDashboard aggregate query — one projection for the overview page."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from wealthos.modules.dashboard.application.queries.get_cash_flow import GetCashFlowQuery
from wealthos.modules.dashboard.application.queries.get_dashboard_summary import (
    GetDashboardSummaryQuery,
)
from wealthos.modules.dashboard.application.queries.get_recent_transactions import (
    GetRecentTransactionsQuery,
)
from wealthos.modules.dashboard.application.queries.period_filters import (
    DashboardPeriodFilters,
)
from wealthos.modules.dashboard.application.views.summary import (
    CurrencyBalanceView,
    CurrencyCashFlowView,
)
from wealthos.modules.dashboard.domain.repositories.dashboard_read_repository import (
    DashboardReadRepository,
)
from wealthos.modules.dashboard.domain.value_objects.dashboard_period import (
    DashboardPeriod,
)
from wealthos.modules.dashboard.schemas.dashboard import (
    ActivityItemData,
    ActivityNamedRef,
    ActivityWidget,
    ActivityWidgetData,
    AttentionItemData,
    AttentionWidget,
    AttentionWidgetData,
    CashFlowPointData,
    CashFlowWidget,
    CashFlowWidgetData,
    DashboardCurrencyMetrics,
    DashboardOrganizationInfo,
    DashboardPeriodInfo,
    DashboardResponse,
    DashboardWidgets,
    FinancialCommitmentsAttentionItem,
    FinancialCommitmentsNextDue,
    FinancialCommitmentsProjection,
    FinancialCommitmentsTotalByCurrency,
    MetricsWidget,
    ModuleLineData,
    ModuleWidget,
    ModuleWidgetData,
    OnboardingStepData,
    OnboardingWidget,
    OnboardingWidgetData,
    SafeToSpendWidget,
    SafeToSpendWidgetData,
    UpcomingWidget,
    UpcomingWidgetData,
    WidgetAction,
)
from wealthos.modules.debts.application.queries.get_debt_summary import GetDebtSummaryQuery
from wealthos.modules.goals.application.queries.get_goals_dashboard_summary import (
    GetGoalsDashboardSummaryQuery,
)
from wealthos.modules.planning.application.queries.get_planning_summary import (
    GetPlanningSummaryQuery,
)
from wealthos.modules.taxes.application.queries.get_tax_summary import GetTaxSummaryQuery
from wealthos.shared.persistence import SqlAlchemyUnitOfWork

logger = logging.getLogger(__name__)

_ZERO = Decimal("0.00")


class GetDashboardQuery:
    def __init__(
        self,
        *,
        summary_query: GetDashboardSummaryQuery,
        cash_flow_query: GetCashFlowQuery,
        recent_query: GetRecentTransactionsQuery,
        repository: DashboardReadRepository,
        goals_query: GetGoalsDashboardSummaryQuery,
        debts_query: GetDebtSummaryQuery,
        taxes_query: GetTaxSummaryQuery,
        planning_query: GetPlanningSummaryQuery,
        uow: SqlAlchemyUnitOfWork,
    ) -> None:
        self._summary_query = summary_query
        self._cash_flow_query = cash_flow_query
        self._recent_query = recent_query
        self._repository = repository
        self._goals_query = goals_query
        self._debts_query = debts_query
        self._taxes_query = taxes_query
        self._planning_query = planning_query
        self._uow = uow

    def execute(
        self,
        organization_id: UUID,
        *,
        organization_name: str,
        timezone: str,
        primary_currency: str,
        filters: DashboardPeriodFilters,
        selected_currency: str | None = None,
    ) -> DashboardResponse:
        summary, date_range = self._summary_query.execute(
            organization_id,
            timezone=timezone,
            primary_currency=primary_currency,
            filters=filters,
        )

        currency = selected_currency or primary_currency
        available = [item.currency for item in summary.balances] or [primary_currency]
        if currency not in available:
            currency = primary_currency if primary_currency in available else available[0]

        flow_by_currency = {item.currency: item for item in summary.cash_flow}
        currencies = [
            self._currency_metrics(balance, flow_by_currency.get(balance.currency))
            for balance in summary.balances
        ]
        if not currencies:
            currencies = [
                DashboardCurrencyMetrics(
                    currency=primary_currency,
                    net_worth=_ZERO,
                    liquid_balance=_ZERO,
                    total_assets=_ZERO,
                    total_liabilities=_ZERO,
                    monthly_income=_ZERO,
                    monthly_expenses=_ZERO,
                    monthly_net_flow=_ZERO,
                )
            ]

        selected_flow = flow_by_currency.get(currency)
        selected_metrics = next(
            (item for item in currencies if item.currency == currency),
            currencies[0],
        )

        planning = self._safe_planning(organization_id)
        onboarding = self._build_onboarding(
            organization_id,
            active_accounts=summary.active_account_count,
            period_income=selected_flow.income if selected_flow else _ZERO,
            period_expenses=selected_flow.expenses if selected_flow else _ZERO,
            has_budget=bool(
                planning
                and (planning["active_budgets"] > 0 or planning["active_cash_plans"] > 0)
            ),
        )
        goals = self._safe_goals(organization_id, currency)
        debts = self._safe_debts(organization_id, currency)
        financial_commitments = self._build_financial_commitments(
            organization_id,
            currency=currency,
        )
        taxes = self._safe_taxes(organization_id, currency)

        attention = self._build_attention(
            currency=currency,
            onboarding=onboarding.data,
            taxes=taxes,
            debts=debts,
            financial_commitments=financial_commitments,
            monthly_income=selected_metrics.monthly_income,
            monthly_expenses=selected_metrics.monthly_expenses,
        )
        activity = self._build_activity(organization_id, currency=currency)
        cash_flow = self._build_cash_flow(
            organization_id,
            timezone=timezone,
            primary_currency=primary_currency,
            selected_currency=currency,
        )
        safe_to_spend = self._build_safe_to_spend(planning)
        budget = self._build_budget(planning)
        goal = self._build_goal(goals)
        debts_widget = self._build_debts_widget(debts)
        taxes_widget = self._build_taxes_widget(taxes)
        upcoming = self._build_upcoming(financial_commitments, currency=currency)

        return DashboardResponse(
            as_of=datetime.now(UTC),
            organization=DashboardOrganizationInfo(
                id=organization_id,
                name=organization_name,
                timezone=timezone,
                currency=primary_currency,
            ),
            period=DashboardPeriodInfo(
                date_from=date_range.display_from,
                date_to=date_range.display_to,
                timezone=date_range.timezone,
            ),
            currencies=currencies,
            selected_currency=currency,
            available_currencies=available,
            widgets=DashboardWidgets(
                metrics=MetricsWidget(status="ready"),
                onboarding=onboarding,
                attention=attention,
                activity=activity,
                cash_flow=cash_flow,
                upcoming=upcoming,
                safe_to_spend=safe_to_spend,
                budget=budget,
                goal=goal,
                debts=debts_widget,
                taxes=taxes_widget,
            ),
            financial_commitments=financial_commitments,
        )

    @staticmethod
    def _currency_metrics(
        balance: CurrencyBalanceView,
        flow: CurrencyCashFlowView | None,
    ) -> DashboardCurrencyMetrics:
        income = flow.income if flow else _ZERO
        expenses = flow.expenses if flow else _ZERO
        return DashboardCurrencyMetrics(
            currency=balance.currency,
            net_worth=balance.net_worth,
            liquid_balance=balance.liquid_balance,
            total_assets=balance.total_assets,
            total_liabilities=balance.total_liabilities,
            monthly_income=income,
            monthly_expenses=expenses,
            monthly_net_flow=flow.net_cash_flow if flow else _ZERO,
        )

    def _build_onboarding(
        self,
        organization_id: UUID,
        *,
        active_accounts: int,
        period_income: Decimal,
        period_expenses: Decimal,
        has_budget: bool,
    ) -> OnboardingWidget:
        has_account = active_accounts > 0
        has_income = period_income > 0 or self._repository.has_posted_transaction_type(
            organization_id,
            transaction_type="income",
        )
        has_expense = period_expenses > 0 or self._repository.has_posted_transaction_type(
            organization_id,
            transaction_type="expense",
        )

        steps = [
            OnboardingStepData(
                id="create_account",
                label="Crea tu primera cuenta",
                description="Checking, ahorro o efectivo para empezar.",
                completed=has_account,
                to="/app/accounts",
            ),
            OnboardingStepData(
                id="record_income",
                label="Registra un ingreso",
                description="Un cobro reciente basta para activar el flujo.",
                completed=has_income,
                to="/app/transactions",
            ),
            OnboardingStepData(
                id="record_expense",
                label="Registra un gasto",
                description="Empieza a ver en qué se va el dinero.",
                completed=has_expense,
                to="/app/transactions",
            ),
            OnboardingStepData(
                id="create_budget",
                label="Crea un presupuesto",
                description="Define cuánto puedes gastar este mes.",
                completed=has_budget,
                to="/app/planning",
            ),
        ]
        core_done = has_account and has_income and has_expense
        completed_steps = sum(1 for step in steps[:3] if step.completed)
        data = OnboardingWidgetData(
            is_visible=not core_done,
            completed=core_done,
            completed_steps=completed_steps,
            total_steps=3,
            steps=steps,
        )
        return OnboardingWidget(
            status="empty" if not data.is_visible else "ready",
            data=data,
        )

    def _build_attention(
        self,
        *,
        currency: str,
        onboarding: OnboardingWidgetData,
        taxes: dict | None,
        debts: dict | None,
        financial_commitments: FinancialCommitmentsProjection | None,
        monthly_income: Decimal,
        monthly_expenses: Decimal,
    ) -> AttentionWidget:
        items: list[AttentionItemData] = []

        tax_balance = taxes.get("balance") if taxes else None
        if tax_balance is not None and tax_balance > 0:
            items.append(
                AttentionItemData(
                    id="tax_balance",
                    severity="warning",
                    title="Impuestos por cubrir",
                    message="Hay un saldo fiscal estimado pendiente este periodo.",
                    amount=tax_balance,
                    currency=currency,
                    action_label="Revisar impuestos",
                    action_to="/app/taxes",
                )
            )

        if financial_commitments and financial_commitments.attention:
            for item in financial_commitments.attention[:5]:
                severity = "critical" if item.code == "overdue" else "warning"
                items.append(
                    AttentionItemData(
                        id=f"commitment_{item.commitment_id}",
                        severity=severity,
                        title="Obligación requiere atención",
                        message=item.message,
                        action_label="Ver obligación",
                        action_to=f"/app/commitments/{item.commitment_id}",
                    )
                )
        elif financial_commitments and financial_commitments.active_count > 0:
            group = next(
                (
                    item
                    for item in financial_commitments.totals_by_currency
                    if item.currency == currency
                ),
                financial_commitments.totals_by_currency[0]
                if financial_commitments.totals_by_currency
                else None,
            )
            items.append(
                AttentionItemData(
                    id="active_debts",
                    severity="info",
                    title="Obligaciones activas",
                    message=(
                        f"Tienes {financial_commitments.active_count} "
                        f"obligación(es) con seguimiento activo."
                    ),
                    amount=group.total_obligations if group else None,
                    currency=currency if group is not None else None,
                    action_label="Ver obligaciones",
                    action_to="/app/commitments",
                )
            )
        else:
            active_debts = debts.get("active_count", 0) if debts else 0
            debt_total = debts.get("total_debt") if debts else None
            if active_debts > 0:
                items.append(
                    AttentionItemData(
                        id="active_debts",
                        severity="info",
                        title="Obligaciones activas",
                        message=f"Tienes {active_debts} obligación(es) con seguimiento activo.",
                        amount=debt_total,
                        currency=currency if debt_total is not None else None,
                        action_label="Ver obligaciones",
                        action_to="/app/commitments",
                    )
                )

        if onboarding.is_visible:
            items.append(
                AttentionItemData(
                    id="onboarding",
                    severity="info",
                    title="Completa tu panorama inicial",
                    message=(
                        f"Llevas {onboarding.completed_steps} de "
                        f"{onboarding.total_steps} pasos. Cada uno revela más "
                        "de tu salud financiera."
                    ),
                    action_label="Ver checklist",
                    action_to="#onboarding",
                )
            )

        if monthly_expenses > monthly_income:
            items.append(
                AttentionItemData(
                    id="cash_shortfall",
                    severity="critical",
                    title="Gastos mayores a ingresos",
                    message="Este mes el flujo de caja es negativo.",
                    amount=monthly_expenses - monthly_income,
                    currency=currency,
                    action_label="Ver flujo",
                    action_to="/app/dashboard",
                )
            )

        severity_rank = {"critical": 0, "warning": 1, "info": 2}
        items.sort(key=lambda item: severity_rank.get(item.severity, 9))
        items = items[:4]
        return AttentionWidget(
            status="ready" if items else "empty",
            data=AttentionWidgetData(items=items),
        )

    def _build_activity(
        self,
        organization_id: UUID,
        *,
        currency: str,
    ) -> ActivityWidget:
        try:
            recent = self._recent_query.execute(organization_id, limit=20)
            items = [
                ActivityItemData(
                    id=item.id,
                    transaction_type=item.transaction_type,
                    description=item.description,
                    category=(
                        ActivityNamedRef(id=item.category.id, name=item.category.name)
                        if item.category
                        else None
                    ),
                    occurred_at=item.occurred_at,
                    status=item.status,
                    amount=item.amount,
                    currency=item.currency,
                    account=(
                        ActivityNamedRef(id=item.account.id, name=item.account.name)
                        if item.account
                        else None
                    ),
                )
                for item in recent
                if item.currency == currency
            ][:8]
            return ActivityWidget(
                status="ready" if items else "empty",
                data=ActivityWidgetData(items=items),
            )
        except Exception:
            logger.exception("dashboard.activity.failed")
            return ActivityWidget(status="error", data=None, error_code="activity_failed")

    def _build_cash_flow(
        self,
        organization_id: UUID,
        *,
        timezone: str,
        primary_currency: str,
        selected_currency: str,
    ) -> CashFlowWidget:
        try:
            series, _, gran = self._cash_flow_query.execute(
                organization_id,
                timezone=timezone,
                primary_currency=primary_currency,
                filters=DashboardPeriodFilters(period=DashboardPeriod("this_month")),
                granularity="day",
            )
            match = next(
                (item for item in series if item.currency == selected_currency),
                series[0] if series else None,
            )
            if match is None or not match.items:
                return CashFlowWidget(status="empty", data=None)

            income = sum((point.income for point in match.items), _ZERO)
            expenses = sum((point.expenses for point in match.items), _ZERO)
            return CashFlowWidget(
                status="ready",
                data=CashFlowWidgetData(
                    currency=match.currency,
                    granularity=gran.value,
                    income=_ZERO + income,
                    expenses=_ZERO + expenses,
                    net_cash_flow=_ZERO + (income - expenses),
                    points=[
                        CashFlowPointData(
                            period_start=point.period_start,
                            income=point.income,
                            expenses=point.expenses,
                            net_cash_flow=point.net_cash_flow,
                        )
                        for point in match.items
                    ],
                ),
            )
        except Exception:
            logger.exception("dashboard.cash_flow.failed")
            return CashFlowWidget(status="error", data=None, error_code="cash_flow_failed")

    def _safe_planning(self, organization_id: UUID) -> dict | None:
        try:
            summary = self._planning_query.execute(organization_id)
            return {
                "active_budgets": summary.active_budgets,
                "active_cash_plans": summary.active_cash_plans,
                "currency": summary.currency,
                "safe_to_spend": summary.safe_to_spend,
                "funding_gap": summary.funding_gap,
            }
        except Exception:
            logger.exception("dashboard.planning.failed")
            return None

    def _safe_goals(self, organization_id: UUID, currency: str) -> dict | None:
        try:
            goals = self._goals_query.execute(organization_id, currency=currency)
            primary = goals.top_goals[0] if goals.top_goals else None
            primary_payload = None
            if primary is not None:
                primary_payload = {
                    "id": primary.goal.id,
                    "name": primary.goal.name.value,
                    "current_amount": primary.progress.current_amount.amount,
                    "target_amount": primary.goal.target_amount.amount,
                    "completion_percentage": primary.progress.completion_percentage,
                    "estimated_completion_date": primary.progress.estimated_completion_date,
                }
            return {
                "active": goals.active_goals,
                "completed": goals.completed_goals,
                "total_target": goals.total_target,
                "current_progress": goals.current_progress,
                "primary": primary_payload,
            }
        except Exception:
            logger.exception("dashboard.goals.failed")
            return None

    def _safe_debts(self, organization_id: UUID, currency: str) -> dict | None:
        try:
            summary = self._debts_query.execute(organization_id)
            primary = next(
                (item for item in summary.by_currency if item.currency == currency),
                None,
            )
            # Never fall back to another currency — that mislabels MXN as USD (P09).
            if primary is None:
                return {
                    "active_count": 0,
                    "total_debt": _ZERO,
                    "minimum_payments": _ZERO,
                }
            return {
                "active_count": primary.active_debt_count,
                "total_debt": primary.total_debt,
                "minimum_payments": primary.total_minimum_payments,
            }
        except Exception:
            logger.exception("dashboard.debts.failed")
            return None

    def _build_financial_commitments(
        self,
        organization_id: UUID,
        *,
        currency: str,
    ) -> FinancialCommitmentsProjection:
        try:
            summary = self._debts_query.execute(organization_id)
            groups = [item for item in summary.by_currency if item.currency == currency]
            attention = [
                item for item in summary.attention if item.currency == currency
            ]
            overdue_count = sum(1 for item in attention if item.code == "overdue")
            active_count = sum(item.active_debt_count for item in groups)

            next_due = None
            per_currency_due = next(
                (item for item in summary.next_due_by_currency if item.currency == currency),
                None,
            )
            if per_currency_due is not None:
                next_due = FinancialCommitmentsNextDue(
                    commitment_id=per_currency_due.commitment_id,
                    name=per_currency_due.name,
                    due_in_days=per_currency_due.days_until_due,
                    currency=per_currency_due.currency,
                    amount=per_currency_due.amount,
                )

            status = "ready" if active_count > 0 else "empty"
            return FinancialCommitmentsProjection(
                status=status,
                active_count=active_count,
                overdue_count=overdue_count,
                totals_by_currency=[
                    FinancialCommitmentsTotalByCurrency(
                        currency=item.currency,
                        total_obligations=item.total_debt,
                        monthly_payments=item.total_minimum_payments,
                    )
                    for item in groups
                ],
                next_due=next_due,
                attention=[
                    FinancialCommitmentsAttentionItem(
                        commitment_id=item.commitment_id,
                        code=item.code,
                        message=item.message,
                        currency=item.currency,
                    )
                    for item in attention
                ],
            )
        except Exception:
            logger.exception("dashboard.financial_commitments.failed")
            return FinancialCommitmentsProjection(
                status="error",
                error_code="commitments_failed",
            )

    @staticmethod
    def _build_upcoming(
        financial_commitments: FinancialCommitmentsProjection,
        *,
        currency: str,
    ) -> UpcomingWidget:
        if financial_commitments.status == "error":
            return UpcomingWidget(status="empty", data=UpcomingWidgetData(items=[]))
        items: list[dict] = []
        if (
            financial_commitments.next_due is not None
            and (
                financial_commitments.next_due.currency is None
                or financial_commitments.next_due.currency == currency
            )
        ):
            nd = financial_commitments.next_due
            items.append(
                {
                    "id": str(nd.commitment_id),
                    "date_label": f"En {nd.due_in_days} día(s)",
                    "description": f"Pago · {nd.name}",
                    "amount": nd.amount,
                    "currency": nd.currency or currency,
                    "status": "attention" if nd.due_in_days <= 7 else "normal",
                    "to": f"/app/commitments/{nd.commitment_id}",
                }
            )
        if not items:
            return UpcomingWidget(status="empty", data=UpcomingWidgetData(items=[]))
        return UpcomingWidget(status="ready", data=UpcomingWidgetData(items=items))

    def _safe_taxes(self, organization_id: UUID, currency: str) -> dict | None:
        try:
            with self._uow:
                summary = self._taxes_query.execute(organization_id)
                self._uow.commit()
            if not summary.has_active_profile:
                return {"configured": False}
            primary = next(
                (item for item in summary.by_currency if item.currency == currency),
                None,
            )
            # Never fall back to another currency — that mislabels amounts (P09).
            if primary is None:
                return {"configured": True, "empty": True}
            return {
                "configured": True,
                "estimated": primary.estimated_tax,
                "paid": primary.paid,
                "balance": primary.balance,
                "cash_like": primary.cash_like_assets,
                "available_after_tax": primary.available_after_tax,
            }
        except Exception:
            logger.exception("dashboard.taxes.failed")
            return None

    @staticmethod
    def _build_safe_to_spend(planning: dict | None) -> SafeToSpendWidget:
        if planning is None:
            return SafeToSpendWidget(
                status="error",
                data=None,
                action=WidgetAction(label="Abrir Planning", to="/app/planning"),
                error_code="planning_failed",
            )
        configured = planning["active_cash_plans"] > 0 or planning["active_budgets"] > 0
        if not configured:
            return SafeToSpendWidget(
                status="not_configured",
                data=None,
                action=WidgetAction(
                    label="Configura tu flujo de caja",
                    to="/app/planning",
                ),
            )
        if planning["safe_to_spend"] is None:
            return SafeToSpendWidget(
                status="unavailable",
                data=SafeToSpendWidgetData(
                    currency=planning["currency"],
                    safe_to_spend=None,
                    funding_gap=planning["funding_gap"],
                ),
                action=WidgetAction(label="Ver Planning", to="/app/planning"),
            )
        return SafeToSpendWidget(
            status="available",
            data=SafeToSpendWidgetData(
                currency=planning["currency"],
                safe_to_spend=planning["safe_to_spend"],
                funding_gap=planning["funding_gap"],
            ),
            action=WidgetAction(label="Ver Planning", to="/app/planning"),
        )

    @staticmethod
    def _build_budget(planning: dict | None) -> ModuleWidget:
        if planning is None:
            return ModuleWidget(
                status="error",
                data=ModuleWidgetData(title="Presupuesto del mes", lines=[]),
                action=WidgetAction(label="Ver Planning", to="/app/planning"),
                error_code="planning_failed",
            )
        if planning["active_budgets"] > 0 or planning["active_cash_plans"] > 0:
            return ModuleWidget(
                status="available",
                data=ModuleWidgetData(
                    title="Presupuesto del mes",
                    lines=[ModuleLineData(label="Estado", value="Planificación activa")],
                    hint="Abre Planning para ver el ritmo de gasto.",
                ),
                action=WidgetAction(label="Ver presupuesto", to="/app/planning"),
            )
        return ModuleWidget(
            status="not_configured",
            data=ModuleWidgetData(
                title="Presupuesto del mes",
                lines=[],
                hint="Crea un presupuesto para controlar tu ritmo de gasto.",
            ),
            action=WidgetAction(label="Crear presupuesto", to="/app/planning"),
        )

    @staticmethod
    def _build_goal(goals: dict | None) -> ModuleWidget:
        if goals is None:
            return ModuleWidget(
                status="error",
                data=ModuleWidgetData(title="Metas", lines=[]),
                action=WidgetAction(label="Ver metas", to="/app/goals"),
                error_code="goals_failed",
            )
        primary = goals.get("primary")
        if primary is not None:
            pct = format(primary["completion_percentage"], "f")
            return ModuleWidget(
                status="available",
                data=ModuleWidgetData(
                    title=primary["name"],
                    lines=[
                        ModuleLineData(
                            label="Progreso",
                            value=format(primary["current_amount"], "f"),
                        ),
                        ModuleLineData(
                            label="Objetivo",
                            value=format(primary["target_amount"], "f"),
                        ),
                        ModuleLineData(label="Avance", value=f"{pct}%"),
                    ],
                    hint=f"{pct}% completado · Meta prioritaria del panorama",
                ),
                action=WidgetAction(
                    label="Ver detalle",
                    to=f"/app/goals/{primary['id']}",
                ),
            )
        if goals["active"] > 0:
            return ModuleWidget(
                status="available",
                data=ModuleWidgetData(
                    title="Metas",
                    lines=[
                        ModuleLineData(label="Activas", value=str(goals["active"])),
                        ModuleLineData(label="Completadas", value=str(goals["completed"])),
                    ],
                ),
                action=WidgetAction(label="Ver metas", to="/app/goals"),
            )
        return ModuleWidget(
            status="not_configured",
            data=ModuleWidgetData(
                title="Metas",
                lines=[],
                hint="Define una meta prioritaria para dar dirección a tu ahorro.",
            ),
            action=WidgetAction(label="Crear meta", to="/app/goals/new"),
        )

    @staticmethod
    def _build_debts_widget(debts: dict | None) -> ModuleWidget:
        if debts is None:
            return ModuleWidget(
                status="error",
                data=ModuleWidgetData(title="Obligaciones", lines=[]),
                action=WidgetAction(label="Ver obligaciones", to="/app/commitments"),
                error_code="debts_failed",
            )
        if debts["active_count"] > 0:
            return ModuleWidget(
                status="available",
                data=ModuleWidgetData(
                    title="Obligaciones",
                    lines=[
                        ModuleLineData(
                            label="Total adeudado",
                            value=format(debts["total_debt"], "f"),
                        ),
                        ModuleLineData(
                            label="Pagos del mes",
                            value=format(debts["minimum_payments"], "f"),
                        ),
                    ],
                ),
                action=WidgetAction(label="Ver obligaciones", to="/app/commitments"),
            )
        return ModuleWidget(
            status="not_configured",
            data=ModuleWidgetData(
                title="Obligaciones",
                lines=[],
                hint="Registra tarjetas y préstamos para ver pagos próximos.",
            ),
            action=WidgetAction(label="Nueva obligación", to="/app/commitments/new"),
        )

    @staticmethod
    def _build_taxes_widget(taxes: dict | None) -> ModuleWidget:
        if taxes is None:
            return ModuleWidget(
                status="error",
                data=ModuleWidgetData(title="Impuestos", lines=[]),
                action=WidgetAction(label="Revisar impuestos", to="/app/taxes"),
                error_code="taxes_failed",
            )
        if not taxes.get("configured"):
            return ModuleWidget(
                status="not_configured",
                data=ModuleWidgetData(
                    title="Impuestos",
                    lines=[],
                    hint="Configura tu perfil fiscal para estimar reservas.",
                ),
                action=WidgetAction(label="Configurar impuestos", to="/app/taxes"),
            )
        if taxes.get("empty"):
            return ModuleWidget(
                status="empty",
                data=ModuleWidgetData(
                    title="Impuestos estimados",
                    lines=[],
                    hint="Aún no hay cálculo para el periodo actual.",
                ),
                action=WidgetAction(label="Revisar cálculo", to="/app/taxes"),
            )
        return ModuleWidget(
            status="available",
            data=ModuleWidgetData(
                title="Impuestos estimados",
                lines=[
                    ModuleLineData(label="Por pagar", value=format(taxes["balance"], "f")),
                    ModuleLineData(label="Pagado", value=format(taxes["paid"], "f")),
                    ModuleLineData(label="Estimado", value=format(taxes["estimated"], "f")),
                ],
            ),
            action=WidgetAction(label="Revisar cálculo", to="/app/taxes"),
        )
