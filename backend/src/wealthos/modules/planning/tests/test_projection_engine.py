"""SPEC-004 acceptance fixtures for the planning projection engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.planning.domain.entities.planning_settings import PlanningSettings
from wealthos.modules.planning.domain.enums.cash_flow import (
    CashFlowCertainty,
    CashFlowDirection,
    CashFlowStatus,
)
from wealthos.modules.planning.domain.enums.planning_horizon import PlanningHorizon
from wealthos.modules.planning.domain.enums.projection import (
    ProjectionConfidence,
    ProjectionStatus,
)
from wealthos.modules.planning.domain.enums.reservation import (
    ReservationType,
    SafetyReserveStrategy,
)
from wealthos.modules.planning.domain.enums.source import PlanningSource
from wealthos.modules.planning.domain.services.horizon_resolver import (
    PlanningHorizonResolver,
)
from wealthos.modules.planning.domain.services.projection_engine import (
    PlanningProjectionEngine,
)
from wealthos.modules.planning.domain.services.scenario_engine import (
    AddCashFlowAdjustment,
    PlanningScenarioEngine,
)
from wealthos.modules.planning.domain.value_objects.account_snapshot import (
    PlanningAccountSnapshot,
)
from wealthos.modules.planning.domain.value_objects.cash_flow import PlanningCashFlow
from wealthos.modules.planning.domain.value_objects.projection_result import (
    PlanningContext,
    ProjectionPeriod,
)
from wealthos.modules.planning.domain.value_objects.reservation import PlanningReservation
from wealthos.modules.planning.domain.value_objects.settlement import PlanningSettlement
from wealthos.modules.planning.domain.value_objects.source_reference import (
    PlanningSourceReference,
)

CURRENCY = "MXN"
CALCULATED_AT = datetime(2026, 8, 1, 15, 0, tzinfo=UTC)


@dataclass
class ProjectionFixture:
    """Builder for deterministic engine contexts."""

    organization_id: UUID = field(default_factory=uuid4)
    currency: str = CURRENCY
    calculated_at: datetime = CALCULATED_AT
    horizon: PlanningHorizon = PlanningHorizon.THIRTY_DAYS
    timezone: str = "UTC"
    accounts: list[PlanningAccountSnapshot] = field(default_factory=list)
    cash_flows: list[PlanningCashFlow] = field(default_factory=list)
    reservations: list[PlanningReservation] = field(default_factory=list)
    settlements: list[PlanningSettlement] = field(default_factory=list)
    reserve_strategy: SafetyReserveStrategy = SafetyReserveStrategy.NONE
    reserve_amount: Decimal | None = None
    include_expected_income: bool = True
    include_estimated_expenses: bool = True
    linked_emergency_goal_id: UUID | None = None

    def with_cash(
        self,
        amount: str,
        *,
        account_type: str = "checking",
        currency: str | None = None,
        included: bool = True,
    ) -> ProjectionFixture:
        code = currency or self.currency
        balance = Decimal(amount)
        self.accounts.append(
            PlanningAccountSnapshot(
                account_id=uuid4(),
                organization_id=self.organization_id,
                name=f"{account_type}-{len(self.accounts) + 1}",
                account_type=account_type,
                currency=code,
                ledger_balance=balance,
                available_balance=balance,
                is_liquid=included,
                is_included=included,
                exclusion_reason=None if included else "non_liquid_account",
                balance_as_of=self.calculated_at,
            )
        )
        return self

    def with_flow(
        self,
        *,
        direction: CashFlowDirection,
        amount: str,
        day_offset: int,
        label: str,
        certainty: CashFlowCertainty = CashFlowCertainty.CONFIRMED,
        source_name: str = PlanningSource.COMMITMENTS.value,
        category: str = "commitment",
        occurrence_key: str | None = None,
        currency: str | None = None,
    ) -> ProjectionFixture:
        value = Decimal(amount)
        key = occurrence_key or f"{source_name}:{len(self.cash_flows) + 1}:day:{day_offset}"
        expected_at = self.calculated_at.replace(
            hour=12, minute=0, second=0, microsecond=0
        ) + timedelta(days=day_offset)
        self.cash_flows.append(
            PlanningCashFlow(
                id=key,
                organization_id=self.organization_id,
                direction=direction,
                amount=value,
                outstanding_amount=value,
                currency=currency or self.currency,
                expected_at=expected_at,
                certainty=certainty,
                status=CashFlowStatus.ACTIVE,
                category=category,
                label=label,
                source=PlanningSourceReference(
                    source_name=source_name,
                    resource_type=category,
                    resource_id=key,
                    occurrence_key=key,
                ),
            )
        )
        return self

    def with_outflow(self, amount: str, day_offset: int, label: str, **kwargs: object) -> ProjectionFixture:
        return self.with_flow(
            direction=CashFlowDirection.OUTFLOW,
            amount=amount,
            day_offset=day_offset,
            label=label,
            **kwargs,  # type: ignore[arg-type]
        )

    def with_inflow(self, amount: str, day_offset: int, label: str, **kwargs: object) -> ProjectionFixture:
        return self.with_flow(
            direction=CashFlowDirection.INFLOW,
            amount=amount,
            day_offset=day_offset,
            label=label,
            **kwargs,  # type: ignore[arg-type]
        )

    def with_fixed_reserve(self, amount: str) -> ProjectionFixture:
        self.reserve_strategy = SafetyReserveStrategy.FIXED_AMOUNT
        self.reserve_amount = Decimal(amount)
        return self

    def with_reservation(
        self,
        *,
        amount: str,
        reservation_type: ReservationType = ReservationType.TAX,
        label: str = "Reserva",
        resource_id: str | None = None,
    ) -> ProjectionFixture:
        key = resource_id or f"{reservation_type.value}:{len(self.reservations) + 1}"
        self.reservations.append(
            PlanningReservation(
                id=key,
                organization_id=self.organization_id,
                reservation_type=reservation_type,
                label=label,
                required_amount=Decimal(amount),
                already_protected_amount=Decimal("0.00"),
                outstanding_amount=Decimal(amount),
                currency=self.currency,
                effective_at=None,
                source=PlanningSourceReference(
                    source_name=reservation_type.value,
                    resource_type=reservation_type.value,
                    resource_id=key,
                    occurrence_key=key,
                ),
            )
        )
        return self

    def with_settlement(self, *, occurrence_key: str, amount: str) -> ProjectionFixture:
        self.settlements.append(
            PlanningSettlement(
                transaction_id=uuid4(),
                organization_id=self.organization_id,
                amount=Decimal(amount),
                currency=self.currency,
                settled_at=self.calculated_at,
                source_occurrence_key=occurrence_key,
            )
        )
        return self

    def build(self) -> PlanningContext:
        period = PlanningHorizonResolver().resolve(
            horizon=self.horizon,
            timezone=self.timezone,
            calculated_at=self.calculated_at,
        )
        settings = PlanningSettings.create(
            organization_id=self.organization_id,
            default_horizon=self.horizon,
            safety_reserve_strategy=self.reserve_strategy,
            safety_reserve_amount=self.reserve_amount,
            linked_emergency_goal_id=self.linked_emergency_goal_id,
            include_expected_income=self.include_expected_income,
            include_estimated_expenses=self.include_estimated_expenses,
        )
        return PlanningContext(
            organization_id=self.organization_id,
            currency=self.currency,
            calculated_at=self.calculated_at,
            period=period,
            settings=settings,
            accounts=tuple(self.accounts),
            cash_flows=tuple(self.cash_flows),
            reservations=tuple(self.reservations),
            settlements=tuple(self.settlements),
        )

    def calculate(self) -> object:
        return PlanningProjectionEngine().calculate(self.build())


def _period_key(period: ProjectionPeriod) -> tuple[str, str]:
    return (period.start_date.isoformat(), period.end_date.isoformat())


# --- Acceptance fixtures (SPEC-004 §9) ---------------------------------------


def test_classic_projection_returns_21700_healthy() -> None:
    """50k − 12k − 6.3k + 30k with a 10k reserve → 21_700 spendable."""
    result = (
        ProjectionFixture()
        .with_cash("50000.00")
        .with_outflow("12000.00", 5, "Renta")
        .with_outflow("6300.00", 10, "Tarjeta HSBC")
        .with_inflow("30000.00", 15, "Nómina")
        .with_fixed_reserve("10000.00")
        .calculate()
    )

    assert result.minimum_projected_balance == Decimal("31700.00")
    assert result.safe_to_spend == Decimal("21700.00")
    assert result.status is ProjectionStatus.HEALTHY
    assert result.projected_ending_balance == Decimal("61700.00")
    assert result.cash_deficit is None
    assert result.reserve_shortfall is None
    assert result.confidence is ProjectionConfidence.HIGH


def test_rent_before_payroll_is_zero_not_ending_balance() -> None:
    """Ending 17k, but the trough after rent is what may be spent today."""
    result = (
        ProjectionFixture()
        .with_cash("10000.00")
        .with_outflow("8000.00", 5, "Renta")
        .with_inflow("15000.00", 15, "Nómina")
        .with_fixed_reserve("2000.00")
        .calculate()
    )

    assert result.minimum_projected_balance == Decimal("2000.00")
    assert result.projected_ending_balance == Decimal("17000.00")
    assert result.safe_to_spend == Decimal("0.00")
    assert result.status is ProjectionStatus.ZERO
    assert result.reserve_shortfall is None


def test_reserve_shortfall_without_negative_cash_is_a_deficit() -> None:
    """Cash stays positive yet dips into protected money → deficit."""
    result = (
        ProjectionFixture()
        .with_cash("10000.00")
        .with_outflow("9000.00", 5, "Pago proveedor")
        .with_fixed_reserve("3000.00")
        .calculate()
    )

    assert result.minimum_projected_balance == Decimal("1000.00")
    assert result.safe_to_spend == Decimal("0.00")
    assert result.status is ProjectionStatus.DEFICIT
    assert result.reserve_shortfall == Decimal("2000.00")
    assert result.cash_deficit is None


def test_no_eligible_accounts_returns_null_safe_to_spend() -> None:
    """`null` means unknown; `0` would mean "computed, no room"."""
    result = ProjectionFixture().calculate()

    assert result.status is ProjectionStatus.INSUFFICIENT_DATA
    assert result.safe_to_spend is None
    assert result.minimum_projected_balance is None
    assert result.projected_ending_balance is None
    assert any(alert.code == "no_eligible_accounts" for alert in result.alerts)


# --- Supporting engine behaviour ---------------------------------------------


def test_only_liquid_accounts_in_the_run_currency_count() -> None:
    result = (
        ProjectionFixture()
        .with_cash("20000.00")
        .with_cash("500000.00", account_type="investment", included=False)
        .with_cash("9000.00", currency="USD")
        .calculate()
    )

    assert result.current_available_cash == Decimal("20000.00")


def test_same_day_outflow_is_processed_before_inflow() -> None:
    result = (
        ProjectionFixture()
        .with_cash("1000.00")
        .with_inflow("5000.00", 3, "Cobro cliente")
        .with_outflow("3000.00", 3, "Pago renta")
        .calculate()
    )

    balances = [point.balance for point in result.timeline]
    assert balances == [Decimal("1000.00"), Decimal("-2000.00"), Decimal("3000.00")]
    assert result.minimum_projected_balance == Decimal("-2000.00")
    assert result.cash_deficit == Decimal("2000.00")
    assert result.status is ProjectionStatus.DEFICIT


def test_estimated_income_never_inflates_safe_to_spend() -> None:
    result = (
        ProjectionFixture()
        .with_cash("10000.00")
        .with_inflow("50000.00", 5, "Bono probable", certainty=CashFlowCertainty.ESTIMATED)
        .calculate()
    )

    assert result.safe_to_spend == Decimal("10000.00")
    assert result.expected_income == Decimal("0.00")
    reasons = {item.reason_code for item in result.excluded_items}
    assert "estimated_income_excluded" in reasons


def test_estimated_expense_is_conservative_by_default() -> None:
    result = (
        ProjectionFixture()
        .with_cash("10000.00")
        .with_outflow("2500.00", 4, "Mantenimiento", certainty=CashFlowCertainty.ESTIMATED)
        .calculate()
    )

    assert result.safe_to_spend == Decimal("7500.00")


def test_settlement_reduces_outstanding_instead_of_double_counting() -> None:
    result = (
        ProjectionFixture()
        .with_cash("10000.00")
        .with_outflow("5000.00", 5, "Pago tarjeta", occurrence_key="commitment:abc:due:2026-08-06")
        .with_settlement(occurrence_key="commitment:abc:due:2026-08-06", amount="2000.00")
        .calculate()
    )

    assert result.committed_outflows == Decimal("3000.00")
    assert result.safe_to_spend == Decimal("7000.00")


def test_reservations_protect_cash_beyond_the_safety_reserve() -> None:
    result = (
        ProjectionFixture()
        .with_cash("10000.00")
        .with_reservation(amount="4000.00", label="Reserva de impuestos")
        .with_fixed_reserve("2000.00")
        .calculate()
    )

    assert result.reserved_funds == Decimal("4000.00")
    assert result.required_minimum_balance == Decimal("6000.00")
    assert result.safe_to_spend == Decimal("4000.00")


def test_flows_outside_the_horizon_are_excluded() -> None:
    result = (
        ProjectionFixture()
        .with_cash("10000.00")
        .with_outflow("9000.00", 45, "Pago fuera de ventana")
        .calculate()
    )

    assert result.safe_to_spend == Decimal("10000.00")
    reasons = {item.reason_code for item in result.excluded_items}
    assert "outside_horizon" in reasons


def test_missing_reserve_caps_confidence_at_medium() -> None:
    result = ProjectionFixture().with_cash("10000.00").calculate()

    assert result.confidence is ProjectionConfidence.MEDIUM
    assert "safety_reserve_not_configured" in result.confidence_reasons


def test_today_horizon_uses_the_org_timezone() -> None:
    fixture = ProjectionFixture()
    fixture.horizon = PlanningHorizon.TODAY
    fixture.timezone = "America/Mexico_City"
    fixture.calculated_at = datetime(2026, 8, 1, 3, 0, tzinfo=UTC)  # 2026-07-31 local
    context = fixture.with_cash("5000.00").build()

    assert _period_key(context.period) == ("2026-07-31", "2026-07-31")


def test_scenario_simulation_does_not_mutate_the_baseline_context() -> None:
    context = (
        ProjectionFixture()
        .with_cash("10000.00")
        .with_fixed_reserve("1000.00")
        .build()
    )
    adjustment = AddCashFlowAdjustment(
        adjustment_id="laptop",
        direction=CashFlowDirection.OUTFLOW,
        amount=Decimal("4000.00"),
        expected_at=CALCULATED_AT + timedelta(days=2),
        label="Compra laptop",
    )

    simulation = PlanningScenarioEngine().simulate(context, (adjustment,))

    assert simulation.baseline.safe_to_spend == Decimal("9000.00")
    assert simulation.scenario.safe_to_spend == Decimal("5000.00")
    assert simulation.impact.safe_to_spend_delta == Decimal("-4000.00")
    assert context.cash_flows == ()
    assert simulation.scenario.included_cash_flows[0].occurrence_key == "scenario:laptop"
