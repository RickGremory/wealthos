import type { ApiClient } from '~/lib/api/types'
import type {
  CommitmentDetailView,
  CommitmentListItemView,
  CommitmentNextActionView,
  CommitmentSummaryView,
  CommitmentStrategyView,
  CreateCommitmentInput,
  PaymentStrategy,
  UpdateCommitmentInput,
} from '~/types/commitments'

interface NextActionDto {
  type: string
  reason_code: string
  amount: string | number | null
  due_date: string | null
}

interface DebtDto {
  id: string
  organization_id: string
  account_id: string
  name: string
  debt_type: string
  creditor: string | null
  currency: string
  priority: string
  interest_rate: string | number | null
  minimum_payment: string | number | null
  scheduled_payment: string | number | null
  credit_limit: string | number | null
  original_amount: string | number | null
  maturity_date: string | null
  due_day: number | null
  statement_day: number | null
  status: string
  display_status: string | null
  behavior: string | null
  notes: string | null
  version: number
  current_balance: string | number
  next_due_date: string | null
  days_until_due: number | null
  utilization_percentage: string | number | null
  next_action: NextActionDto | null
  created_at: string
  updated_at: string
  closed_at: string | null
  archived_at: string | null
}

interface DebtListDto {
  items: DebtDto[]
  total: number
}

interface SummaryDto {
  by_currency: Array<{
    currency: string
    total_debt: string | number
    total_minimum_payments: string | number
    weighted_average_rate: string | number
    active_debt_count: number
    highest_interest_debt_id: string | null
    highest_interest_rate: string | number | null
  }>
  groups?: Array<{
    currency: string
    total_debt: string | number
    total_minimum_payments: string | number
    weighted_average_rate: string | number
    active_debt_count: number
    highest_interest_debt_id: string | null
    highest_interest_rate: string | number | null
  }>
  active_commitments: number
  commitments_needing_attention: number
  next_due: {
    commitment_id: string
    name: string
    currency: string
    due_date: string
    days_until_due: number
    amount: string | number | null
  } | null
}

interface StrategyDto {
  status: string
  strategy: string
  generated_at: string
  summary: {
    active_commitments: number
    total_balance: string | number
    currency: string
  } | null
  next_action: {
    type: string
    commitment_id: string | null
    amount: string | number | null
    due_date: string | null
    reason_code: string
  } | null
  ranking: Array<{
    position: number
    commitment_id: string
    name: string
    reason_code: string
    eligible: boolean
  }>
  warnings: string[]
  excluded_commitments: number
}

function toDecimalString(value: string | number | null | undefined): string | null {
  if (value == null) return null
  if (typeof value === 'number') return value.toFixed(2)
  const trimmed = String(value).trim()
  return trimmed || null
}

function toRequiredDecimal(value: string | number | null | undefined): string {
  return toDecimalString(value) ?? '0.00'
}

function mapNextAction(dto: NextActionDto | null | undefined): CommitmentNextActionView | null {
  if (!dto) return null
  return {
    type: dto.type as CommitmentNextActionView['type'],
    reasonCode: dto.reason_code,
    amount: toDecimalString(dto.amount),
    dueDate: dto.due_date,
  }
}

/** @internal Exported for unit tests. */
export function mapCommitmentDto(dto: DebtDto): CommitmentListItemView {
  return {
    id: dto.id,
    organizationId: dto.organization_id,
    accountId: dto.account_id,
    name: dto.name,
    debtType: dto.debt_type as CommitmentListItemView['debtType'],
    creditor: dto.creditor,
    currency: dto.currency,
    priority: (dto.priority as CommitmentListItemView['priority']) || 'medium',
    interestRate: toDecimalString(dto.interest_rate),
    minimumPayment: toDecimalString(dto.minimum_payment),
    scheduledPayment: toDecimalString(dto.scheduled_payment),
    creditLimit: toDecimalString(dto.credit_limit),
    originalAmount: toDecimalString(dto.original_amount),
    maturityDate: dto.maturity_date,
    dueDay: dto.due_day,
    statementDay: dto.statement_day,
    status: (dto.status as CommitmentListItemView['status']) || 'active',
    displayStatus: (dto.display_status as CommitmentListItemView['displayStatus']) || 'active',
    behavior: dto.behavior,
    notes: dto.notes,
    version: dto.version,
    currentBalance: toRequiredDecimal(dto.current_balance),
    nextDueDate: dto.next_due_date,
    daysUntilDue: dto.days_until_due,
    utilizationPercentage: toDecimalString(dto.utilization_percentage),
    nextAction: mapNextAction(dto.next_action),
    createdAt: dto.created_at,
    updatedAt: dto.updated_at,
    closedAt: dto.closed_at,
    archivedAt: dto.archived_at,
  }
}

function mapSummary(dto: SummaryDto): CommitmentSummaryView {
  const groupsSrc = dto.groups?.length ? dto.groups : dto.by_currency
  return {
    groups: (groupsSrc ?? []).map(g => ({
      currency: g.currency,
      totalDebt: toRequiredDecimal(g.total_debt),
      totalMinimumPayments: toRequiredDecimal(g.total_minimum_payments),
      weightedAverageRate: toDecimalString(g.weighted_average_rate) ?? '0.000000',
      activeDebtCount: g.active_debt_count,
      highestInterestDebtId: g.highest_interest_debt_id,
      highestInterestRate: toDecimalString(g.highest_interest_rate),
    })),
    activeCommitments: dto.active_commitments ?? 0,
    commitmentsNeedingAttention: dto.commitments_needing_attention ?? 0,
    nextDue: dto.next_due
      ? {
          commitmentId: dto.next_due.commitment_id,
          name: dto.next_due.name,
          currency: dto.next_due.currency,
          dueDate: dto.next_due.due_date,
          daysUntilDue: dto.next_due.days_until_due,
          amount: toDecimalString(dto.next_due.amount),
        }
      : null,
  }
}

function mapStrategy(dto: StrategyDto): CommitmentStrategyView {
  return {
    status: dto.status,
    strategy: dto.strategy as PaymentStrategy,
    generatedAt: dto.generated_at,
    summary: dto.summary
      ? {
          activeCommitments: dto.summary.active_commitments,
          totalBalance: toRequiredDecimal(dto.summary.total_balance),
          currency: dto.summary.currency,
        }
      : null,
    nextAction: dto.next_action
      ? {
          type: dto.next_action.type,
          commitmentId: dto.next_action.commitment_id,
          amount: toDecimalString(dto.next_action.amount),
          dueDate: dto.next_action.due_date,
          reasonCode: dto.next_action.reason_code,
        }
      : null,
    ranking: (dto.ranking ?? []).map(r => ({
      position: r.position,
      commitmentId: r.commitment_id,
      name: r.name,
      reasonCode: r.reason_code,
      eligible: r.eligible,
    })),
    warnings: dto.warnings ?? [],
    excludedCommitments: dto.excluded_commitments ?? 0,
  }
}

export function createCommitmentsRepository(api: ApiClient) {
  const base = (organizationId: string) => `/organizations/${organizationId}/debts`

  return {
    async list(
      organizationId: string,
      filters?: {
        status?: string
        debtType?: string
        currency?: string
        includeArchived?: boolean
      },
    ): Promise<CommitmentListItemView[]> {
      const params = new URLSearchParams()
      if (filters?.status) params.set('status', filters.status)
      if (filters?.debtType) params.set('debt_type', filters.debtType)
      if (filters?.currency) params.set('currency', filters.currency)
      if (filters?.includeArchived) params.set('include_archived', 'true')
      const qs = params.toString()
      const dto = await api.get<DebtListDto>(`${base(organizationId)}${qs ? `?${qs}` : ''}`)
      return (dto.items ?? []).map(mapCommitmentDto)
    },

    async get(organizationId: string, commitmentId: string): Promise<CommitmentDetailView> {
      const dto = await api.get<DebtDto>(`${base(organizationId)}/${commitmentId}`)
      return mapCommitmentDto(dto)
    },

    async summary(organizationId: string): Promise<CommitmentSummaryView> {
      const dto = await api.get<SummaryDto>(`${base(organizationId)}/summary`)
      return mapSummary(dto)
    },

    async getStrategy(
      organizationId: string,
      currency?: string,
    ): Promise<CommitmentStrategyView> {
      const params = new URLSearchParams()
      if (currency) params.set('currency', currency)
      const qs = params.toString()
      const dto = await api.get<StrategyDto>(
        `${base(organizationId)}/strategy${qs ? `?${qs}` : ''}`,
      )
      return mapStrategy(dto)
    },

    async updateStrategy(
      organizationId: string,
      strategy: PaymentStrategy,
    ): Promise<CommitmentStrategyView> {
      const dto = await api.patch<StrategyDto>(`${base(organizationId)}/strategy`, { strategy })
      return mapStrategy(dto)
    },

    async create(
      organizationId: string,
      input: CreateCommitmentInput,
    ): Promise<CommitmentDetailView> {
      const body: Record<string, unknown> = {
        account_id: input.accountId,
        name: input.name,
        debt_type: input.debtType,
        creditor: input.creditor ?? null,
        priority: input.priority ?? 'medium',
        interest_rate: input.interestRate ?? null,
        minimum_payment: input.minimumPayment ?? null,
        scheduled_payment: input.scheduledPayment ?? null,
        credit_limit: input.creditLimit ?? null,
        original_amount: input.originalAmount ?? null,
        maturity_date: input.maturityDate ?? null,
        due_day: input.dueDay ?? null,
        statement_day: input.statementDay ?? null,
        notes: input.notes ?? null,
      }
      const dto = await api.post<DebtDto>(base(organizationId), body)
      return mapCommitmentDto(dto)
    },

    async update(
      organizationId: string,
      commitmentId: string,
      input: UpdateCommitmentInput,
    ): Promise<CommitmentDetailView> {
      const body: Record<string, unknown> = { version: input.version }
      if (input.name !== undefined) body.name = input.name
      if (input.creditor !== undefined) body.creditor = input.creditor
      if (input.priority !== undefined) body.priority = input.priority
      if (input.interestRate !== undefined) body.interest_rate = input.interestRate
      if (input.minimumPayment !== undefined) body.minimum_payment = input.minimumPayment
      if (input.scheduledPayment !== undefined) body.scheduled_payment = input.scheduledPayment
      if (input.creditLimit !== undefined) body.credit_limit = input.creditLimit
      if (input.maturityDate !== undefined) body.maturity_date = input.maturityDate
      if (input.dueDay !== undefined) body.due_day = input.dueDay
      if (input.statementDay !== undefined) body.statement_day = input.statementDay
      if (input.notes !== undefined) body.notes = input.notes

      const dto = await api.patch<DebtDto>(`${base(organizationId)}/${commitmentId}`, body)
      return mapCommitmentDto(dto)
    },

    async pause(organizationId: string, commitmentId: string): Promise<CommitmentDetailView> {
      const dto = await api.post<DebtDto>(`${base(organizationId)}/${commitmentId}/pause`, {})
      return mapCommitmentDto(dto)
    },

    async resume(organizationId: string, commitmentId: string): Promise<CommitmentDetailView> {
      const dto = await api.post<DebtDto>(`${base(organizationId)}/${commitmentId}/resume`, {})
      return mapCommitmentDto(dto)
    },

    async close(organizationId: string, commitmentId: string): Promise<CommitmentDetailView> {
      const dto = await api.post<DebtDto>(`${base(organizationId)}/${commitmentId}/close`, {})
      return mapCommitmentDto(dto)
    },

    async archive(organizationId: string, commitmentId: string): Promise<CommitmentDetailView> {
      const dto = await api.post<DebtDto>(`${base(organizationId)}/${commitmentId}/archive`, {})
      return mapCommitmentDto(dto)
    },

    async activity(
      organizationId: string,
      commitmentId: string,
      opts?: { limit?: number, offset?: number },
    ) {
      const params = new URLSearchParams()
      if (opts?.limit) params.set('limit', String(opts.limit))
      if (opts?.offset) params.set('offset', String(opts.offset))
      const qs = params.toString()
      return api.get<{
        items: Array<Record<string, unknown>>
        total: number
        limit: number
        offset: number
      }>(`${base(organizationId)}/${commitmentId}/activity${qs ? `?${qs}` : ''}`)
    },

    async calendarEvents(
      organizationId: string,
      opts?: { dateFrom?: string, dateTo?: string },
    ): Promise<Array<{
      id: string
      commitmentId: string
      name: string
      eventType: string
      eventDate: string
      severity: string
      currency: string
      amount: string | null
    }>> {
      const params = new URLSearchParams()
      if (opts?.dateFrom) params.set('date_from', opts.dateFrom)
      if (opts?.dateTo) params.set('date_to', opts.dateTo)
      const qs = params.toString()
      const dto = await api.get<{
        items: Array<{
          id: string
          commitment_id: string
          name: string
          event_type: string
          event_date: string
          severity: string
          currency: string
          amount: string | number | null
        }>
      }>(`${base(organizationId)}/calendar-events${qs ? `?${qs}` : ''}`)
      return (dto.items ?? []).map(item => ({
        id: item.id,
        commitmentId: item.commitment_id,
        name: item.name,
        eventType: item.event_type,
        eventDate: item.event_date,
        severity: item.severity,
        currency: item.currency,
        amount: item.amount == null ? null : String(item.amount),
      }))
    },
  }
}

export type CommitmentsRepository = ReturnType<typeof createCommitmentsRepository>
