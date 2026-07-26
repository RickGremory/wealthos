import type { ApiClient } from '~/lib/api/types'
import type {
  CreatePlannedCashFlowInput,
  PlannedCashFlow,
  PlanningHorizon,
  PlanningProjection,
  PlanningSettings,
  SafeToSpendSummary,
  ScenarioAdjustmentInput,
  ScenarioSimulation,
  UpdatePlanningSettingsInput,
} from '~/types/planning'

function money(value: string | number | null | undefined): string | null {
  if (value == null) return null
  return typeof value === 'number' ? value.toFixed(2) : String(value)
}

function mapProjection(dto: Record<string, any>): PlanningProjection {
  return {
    organizationId: String(dto.organization_id),
    currency: dto.currency,
    horizon: dto.horizon,
    periodStart: dto.period_start,
    periodEnd: dto.period_end,
    calculatedAt: dto.calculated_at,
    status: dto.status,
    confidence: dto.confidence,
    confidenceReasons: dto.confidence_reasons ?? [],
    currentAvailableCash: money(dto.current_available_cash) || '0.00',
    expectedIncome: money(dto.expected_income) || '0.00',
    committedOutflows: money(dto.committed_outflows) || '0.00',
    protectedFunds: money(dto.protected_funds) || '0.00',
    safeToSpend: money(dto.safe_to_spend),
    projectedEndingBalance: money(dto.projected_ending_balance),
    minimumProjectedBalance: money(dto.minimum_projected_balance),
    lowestBalanceAt: dto.lowest_balance_at ?? null,
    cashDeficit: money(dto.cash_deficit),
    reserveShortfall: money(dto.reserve_shortfall),
    timeline: (dto.timeline ?? []).map((point: Record<string, any>) => ({
      occurredAt: point.occurred_at,
      amount: money(point.amount) || '0.00',
      balanceAfter: money(point.balance_after) || '0.00',
      cashFlowId: point.cash_flow_id ?? null,
      occurrenceKey: point.occurrence_key ?? null,
      label: point.label,
      category: point.category,
      direction: point.direction ?? null,
    })),
    breakdown: (dto.breakdown ?? []).map((item: Record<string, any>) => ({
      id: item.id,
      category: item.category,
      label: item.label,
      amount: money(item.amount) || '0.00',
      currency: item.currency,
      date: item.date ?? null,
      direction: item.direction,
      sourceName: item.source_name,
      sourceId: item.source_id ?? null,
      certainty: item.certainty ?? null,
      included: Boolean(item.included),
      exclusionReason: item.exclusion_reason ?? null,
    })),
    alerts: (dto.alerts ?? []).map((alert: Record<string, any>) => ({
      code: alert.code,
      severity: alert.severity,
      messageKey: alert.message_key,
      relatedResourceType: alert.related_resource_type ?? null,
      relatedResourceId: alert.related_resource_id ?? null,
      date: alert.date ?? null,
      amount: money(alert.amount),
      currency: alert.currency ?? null,
    })),
  }
}

function mapCashFlow(dto: Record<string, any>): PlannedCashFlow {
  return {
    id: String(dto.id),
    organizationId: String(dto.organization_id),
    name: dto.name,
    direction: dto.direction,
    amount: money(dto.amount) || '0.00',
    currency: dto.currency,
    expectedAt: dto.expected_at,
    certainty: dto.certainty,
    status: dto.status,
    notes: dto.notes ?? null,
    version: dto.version,
  }
}

function mapSettings(dto: Record<string, any>): PlanningSettings {
  return {
    id: String(dto.id),
    organizationId: String(dto.organization_id),
    defaultHorizon: dto.default_horizon,
    safetyReserveStrategy: dto.safety_reserve_strategy,
    safetyReserveAmount: money(dto.safety_reserve_amount),
    linkedEmergencyGoalId: dto.linked_emergency_goal_id
      ? String(dto.linked_emergency_goal_id)
      : null,
    includeExpectedIncome: Boolean(dto.include_expected_income),
    includeEstimatedExpenses: Boolean(dto.include_estimated_expenses),
    version: dto.version,
  }
}

export function createPlanningRepository(api: ApiClient) {
  const base = (organizationId: string) =>
    `/organizations/${organizationId}/planning`

  return {
    async getProjection(
      organizationId: string,
      params: { currency: string, horizon?: PlanningHorizon },
    ): Promise<PlanningProjection> {
      const dto = await api.get<Record<string, any>>(`${base(organizationId)}/projection`, {
        query: {
          currency: params.currency,
          ...(params.horizon ? { horizon: params.horizon } : {}),
        },
      })
      return mapProjection(dto)
    },

    async getSafeToSpend(
      organizationId: string,
      params: { currency: string, horizon?: PlanningHorizon },
    ): Promise<SafeToSpendSummary> {
      const dto = await api.get<Record<string, any>>(`${base(organizationId)}/safe-to-spend`, {
        query: {
          currency: params.currency,
          ...(params.horizon ? { horizon: params.horizon } : {}),
        },
      })
      return {
        organizationId: String(dto.organization_id),
        currency: dto.currency,
        horizon: dto.horizon,
        safeToSpend: money(dto.safe_to_spend),
        status: dto.status,
        confidence: dto.confidence,
        reserveShortfall: money(dto.reserve_shortfall) || '0.00',
        cashDeficit: money(dto.cash_deficit) || '0.00',
        lowestBalanceAt: dto.lowest_balance_at ?? null,
        calculatedAt: dto.calculated_at,
      }
    },

    async getSettings(organizationId: string): Promise<PlanningSettings> {
      const dto = await api.get<Record<string, any>>(`${base(organizationId)}/settings`)
      return mapSettings(dto)
    },

    async updateSettings(
      organizationId: string,
      input: UpdatePlanningSettingsInput,
    ): Promise<PlanningSettings> {
      const dto = await api.put<Record<string, any>>(`${base(organizationId)}/settings`, {
        version: input.version ?? undefined,
        default_horizon: input.defaultHorizon,
        safety_reserve_strategy: input.safetyReserveStrategy,
        safety_reserve_amount: input.safetyReserveAmount ?? null,
        linked_emergency_goal_id: input.linkedEmergencyGoalId ?? null,
        include_expected_income: input.includeExpectedIncome,
        include_estimated_expenses: input.includeEstimatedExpenses,
      })
      return mapSettings(dto)
    },

    async listCashFlows(
      organizationId: string,
      params: { currency?: string, status?: string } = {},
    ): Promise<PlannedCashFlow[]> {
      const dto = await api.get<Record<string, any>[]>(`${base(organizationId)}/cash-flows`, {
        query: {
          ...(params.currency ? { currency: params.currency } : {}),
          ...(params.status ? { status: params.status } : {}),
        },
      })
      return (dto ?? []).map(mapCashFlow)
    },

    async createCashFlow(
      organizationId: string,
      input: CreatePlannedCashFlowInput,
    ): Promise<PlannedCashFlow> {
      const dto = await api.post<Record<string, any>>(`${base(organizationId)}/cash-flows`, {
        name: input.name,
        direction: input.direction,
        amount: input.amount,
        currency: input.currency,
        expected_at: input.expectedAt,
        certainty: input.certainty,
        notes: input.notes ?? null,
      })
      return mapCashFlow(dto)
    },

    async cancelCashFlow(organizationId: string, cashFlowId: string): Promise<PlannedCashFlow> {
      const dto = await api.delete<Record<string, any>>(
        `${base(organizationId)}/cash-flows/${cashFlowId}`,
      )
      return mapCashFlow(dto)
    },

    async simulate(
      organizationId: string,
      params: {
        currency: string
        horizon?: PlanningHorizon
        adjustments: ScenarioAdjustmentInput[]
      },
    ): Promise<ScenarioSimulation> {
      const dto = await api.post<Record<string, any>>(
        `${base(organizationId)}/scenarios/simulate`,
        {
          currency: params.currency,
          horizon: params.horizon ?? null,
          adjustments: params.adjustments.map(item => ({
            kind: item.kind,
            direction: item.direction,
            amount: item.amount,
            expected_at: item.expectedAt,
            label: item.label,
            certainty: item.certainty ?? 'expected',
          })),
        },
      )
      return {
        baseline: mapProjection(dto.baseline),
        scenario: mapProjection(dto.scenario),
        impact: {
          safeToSpendBefore: money(dto.impact?.safe_to_spend_before),
          safeToSpendAfter: money(dto.impact?.safe_to_spend_after),
          safeToSpendDelta: money(dto.impact?.safe_to_spend_delta),
          minimumBalanceBefore: money(dto.impact?.minimum_balance_before),
          minimumBalanceAfter: money(dto.impact?.minimum_balance_after),
          minimumBalanceDelta: money(dto.impact?.minimum_balance_delta),
          statusBefore: dto.impact?.status_before,
          statusAfter: dto.impact?.status_after,
          statusChanged: Boolean(dto.impact?.status_changed),
        },
      }
    },
  }
}
