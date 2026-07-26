export type PlanningHorizon = 'today' | '7_days' | '30_days' | '90_days'

export type ProjectionStatus =
  | 'healthy'
  | 'limited'
  | 'zero'
  | 'deficit'
  | 'insufficient_data'
  | 'unavailable'

export type ProjectionConfidence = 'high' | 'medium' | 'low'

export type CashFlowDirection = 'inflow' | 'outflow'
export type CashFlowCertainty = 'confirmed' | 'expected' | 'estimated'
export type CashFlowStatus = 'active' | 'settled' | 'cancelled' | 'expired'

export interface PlanningAlert {
  code: string
  severity: 'info' | 'warning' | 'critical'
  messageKey: string
  relatedResourceType: string | null
  relatedResourceId: string | null
  date: string | null
  amount: string | null
  currency: string | null
}

export interface PlanningBreakdownItem {
  id: string
  category: string
  label: string
  amount: string
  currency: string
  date: string | null
  direction: string
  sourceName: string
  sourceId: string | null
  certainty: CashFlowCertainty | null
  included: boolean
  exclusionReason: string | null
}

export interface PlanningProjectionPoint {
  occurredAt: string
  amount: string
  balanceAfter: string
  cashFlowId: string | null
  occurrenceKey: string | null
  label: string
  category: string
  direction: CashFlowDirection | null
}

export interface PlanningProjection {
  organizationId: string
  currency: string
  horizon: PlanningHorizon
  periodStart: string
  periodEnd: string
  calculatedAt: string
  status: ProjectionStatus
  confidence: ProjectionConfidence
  confidenceReasons: string[]
  currentAvailableCash: string
  expectedIncome: string
  committedOutflows: string
  protectedFunds: string
  safeToSpend: string | null
  projectedEndingBalance: string | null
  minimumProjectedBalance: string | null
  lowestBalanceAt: string | null
  cashDeficit: string | null
  reserveShortfall: string | null
  timeline: PlanningProjectionPoint[]
  breakdown: PlanningBreakdownItem[]
  alerts: PlanningAlert[]
}

export interface SafeToSpendSummary {
  organizationId: string
  currency: string
  horizon: PlanningHorizon
  safeToSpend: string | null
  status: ProjectionStatus
  confidence: ProjectionConfidence
  reserveShortfall: string
  cashDeficit: string
  lowestBalanceAt: string | null
  calculatedAt: string
}

export interface PlanningSettings {
  id: string
  organizationId: string
  defaultHorizon: PlanningHorizon
  safetyReserveStrategy: string
  safetyReserveAmount: string | null
  linkedEmergencyGoalId: string | null
  includeExpectedIncome: boolean
  includeEstimatedExpenses: boolean
  version: number
}

export interface PlannedCashFlow {
  id: string
  organizationId: string
  name: string
  direction: CashFlowDirection
  amount: string
  currency: string
  expectedAt: string
  certainty: CashFlowCertainty
  status: CashFlowStatus
  notes: string | null
  version: number
}

export interface CreatePlannedCashFlowInput {
  name: string
  direction: CashFlowDirection
  amount: string
  currency: string
  expectedAt: string
  certainty: CashFlowCertainty
  notes?: string | null
}

export interface UpdatePlanningSettingsInput {
  version?: number | null
  defaultHorizon: PlanningHorizon
  safetyReserveStrategy: string
  safetyReserveAmount?: string | null
  linkedEmergencyGoalId?: string | null
  includeExpectedIncome: boolean
  includeEstimatedExpenses: boolean
}

export interface ScenarioAdjustmentInput {
  kind: 'add_cash_flow'
  direction: CashFlowDirection
  amount: string
  expectedAt: string
  label: string
  certainty?: CashFlowCertainty
}

export interface ScenarioSimulation {
  baseline: PlanningProjection
  scenario: PlanningProjection
  impact: {
    safeToSpendBefore: string | null
    safeToSpendAfter: string | null
    safeToSpendDelta: string | null
    minimumBalanceBefore: string | null
    minimumBalanceAfter: string | null
    minimumBalanceDelta: string | null
    statusBefore: ProjectionStatus
    statusAfter: ProjectionStatus
    statusChanged: boolean
  }
}
