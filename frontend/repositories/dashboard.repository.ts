import type { ApiClient } from '~/lib/api/types'
import type {
  DashboardAttentionItem,
  DashboardCashFlowSummary,
  DashboardCurrencySlice,
  DashboardModuleSummary,
  DashboardOnboarding,
  DashboardProjection,
  DashboardRecentTransaction,
  DashboardSafeToSpend,
  DashboardWidgetErrorState,
} from '~/types/dashboard'

interface NamedRefDto {
  id: string
  name: string
}

interface CurrencyMetricsDto {
  currency: string
  net_worth: string
  liquid_balance: string
  total_assets: string
  total_liabilities: string
  monthly_income: string
  monthly_expenses: string
  monthly_net_flow: string
}

interface OnboardingStepDto {
  id: string
  label: string
  description: string
  completed: boolean
  to: string
}

interface AttentionItemDto {
  id: string
  severity: 'info' | 'warning' | 'critical'
  title: string
  message: string
  amount?: string | null
  currency?: string | null
  action_label: string
  action_to: string
}

interface ActivityItemDto {
  id: string
  transaction_type: string
  description: string
  category: NamedRefDto | null
  occurred_at: string
  status: string
  amount: string
  currency: string
  account: NamedRefDto | null
}

interface CashFlowPointDto {
  period_start: string
  income: string
  expenses: string
  net_cash_flow: string
}

interface ModuleLineDto {
  label: string
  value: string
}

interface ModuleWidgetDto {
  status: string
  data: {
    title: string
    lines: ModuleLineDto[]
    hint?: string | null
  } | null
  action?: { label: string, to: string } | null
  error_code?: string | null
}

interface DashboardAggregateDto {
  as_of: string
  organization: {
    id: string
    name: string
    timezone: string
    currency: string
  }
  period: {
    date_from: string
    date_to: string
    timezone: string
  }
  currencies: CurrencyMetricsDto[]
  selected_currency: string
  available_currencies: string[]
  widgets: {
    metrics: { status: 'ready' }
    onboarding: {
      status: 'ready' | 'empty'
      data: {
        is_visible: boolean
        completed: boolean
        completed_steps: number
        total_steps: number
        steps: OnboardingStepDto[]
      }
    }
    attention: {
      status: 'ready' | 'empty'
      data: { items: AttentionItemDto[] }
    }
    activity: {
      status: 'ready' | 'empty' | 'error'
      data: { items: ActivityItemDto[] } | null
      error_code?: string | null
    }
    cash_flow: {
      status: 'ready' | 'empty' | 'error'
      data: {
        currency: string
        granularity: string
        income: string
        expenses: string
        net_cash_flow: string
        points: CashFlowPointDto[]
      } | null
      error_code?: string | null
    }
    upcoming: {
      status: 'not_configured' | 'empty' | 'ready'
      data: {
        items: Array<{
          id: string
          date_label?: string
          description?: string
          amount?: string | null
          currency?: string | null
          status?: string
          to?: string
        }>
      }
    }
    safe_to_spend: {
      status: 'available' | 'not_configured' | 'unavailable' | 'error'
      data: {
        currency: string | null
        safe_to_spend: string | null
        funding_gap?: string | null
      } | null
      action?: { label: string, to: string } | null
      error_code?: string | null
    }
    budget: ModuleWidgetDto
    goal: ModuleWidgetDto
    debts: ModuleWidgetDto
    taxes: ModuleWidgetDto
  }
  financial_commitments?: {
    status: 'ready' | 'empty' | 'error'
    active_count: number
    overdue_count: number
    totals_by_currency: Array<{
      currency: string
      total_obligations: string | number
      monthly_payments: string | number
    }>
    next_due: {
      commitment_id: string
      name: string
      due_in_days: number
      currency?: string | null
      amount?: string | number | null
    } | null
    attention: Array<{
      commitment_id: string
      code: string
      message: string
      currency?: string | null
    }>
    error_code?: string | null
  } | null
}

/** @internal Exported for unit tests. */
export function mapDashboardAggregate(dto: DashboardAggregateDto): DashboardProjection {
  const currencies: DashboardCurrencySlice[] = (dto.currencies ?? []).map(item => ({
    currency: item.currency,
    netWorth: String(item.net_worth ?? '0.00'),
    liquidBalance: String(item.liquid_balance ?? '0.00'),
    totalAssets: String(item.total_assets ?? '0.00'),
    totalLiabilities: String(item.total_liabilities ?? '0.00'),
    monthlyIncome: String(item.monthly_income ?? '0.00'),
    monthlyExpenses: String(item.monthly_expenses ?? '0.00'),
    monthlyNetFlow: String(item.monthly_net_flow ?? '0.00'),
  }))

  const onboardingDto = dto.widgets.onboarding
  const onboarding: DashboardOnboarding = {
    isVisible: Boolean(onboardingDto.data.is_visible),
    completed: Boolean(onboardingDto.data.completed),
    completedSteps: onboardingDto.data.completed_steps,
    totalSteps: onboardingDto.data.total_steps,
    status: onboardingDto.status,
    steps: (onboardingDto.data.steps ?? []).map(step => ({
      id: step.id,
      label: step.label,
      description: step.description,
      completed: step.completed,
      to: step.to,
    })),
  }

  const attentionItems: DashboardAttentionItem[] = (dto.widgets.attention.data.items ?? []).map(
    item => ({
      id: item.id,
      severity: item.severity,
      title: item.title,
      message: item.message,
      amount: item.amount != null ? String(item.amount) : null,
      currency: item.currency ?? undefined,
      actionLabel: item.action_label,
      actionTo: item.action_to,
    }),
  )

  const activityItems = dto.widgets.activity.data?.items ?? []
  const recentTransactions: DashboardRecentTransaction[] = activityItems.map(item => ({
    id: item.id,
    description: item.description,
    transactionType: item.transaction_type,
    amount: String(item.amount),
    currency: item.currency,
    occurredAt: item.occurred_at,
    categoryName: item.category?.name ?? null,
    accountName: item.account?.name ?? null,
    status: item.status,
  }))

  const cashDto = dto.widgets.cash_flow
  const cashFlow: DashboardCashFlowSummary = cashDto.status === 'ready' && cashDto.data
    ? {
        status: 'ready',
        currency: cashDto.data.currency,
        income: String(cashDto.data.income),
        expenses: String(cashDto.data.expenses),
        netCashFlow: String(cashDto.data.net_cash_flow),
        points: (cashDto.data.points ?? []).map(point => ({
          periodStart: point.period_start,
          income: String(point.income),
          expenses: String(point.expenses),
          netCashFlow: String(point.net_cash_flow),
        })),
      }
    : {
        status: cashDto.status,
        currency: null,
        income: null,
        expenses: null,
        netCashFlow: null,
        points: [],
        errorCode: cashDto.error_code ?? null,
      }

  const sts = dto.widgets.safe_to_spend
  const safeToSpend: DashboardSafeToSpend = {
    status: sts.status,
    amount: sts.status === 'available' && sts.data?.safe_to_spend != null
      ? String(sts.data.safe_to_spend)
      : null,
    currency: sts.data?.currency ?? null,
    fundingGap: sts.data?.funding_gap != null ? String(sts.data.funding_gap) : null,
    ctaLabel: sts.action?.label,
    ctaTo: sts.action?.to,
    errorCode: sts.error_code ?? null,
  }

  const widgetErrors: DashboardWidgetErrorState[] = []
  if (dto.widgets.activity.status === 'error') {
    widgetErrors.push({
      id: 'activity',
      title: 'Actividad reciente',
      message: 'No se pudieron cargar los movimientos recientes.',
    })
  }
  if (dto.widgets.cash_flow.status === 'error') {
    widgetErrors.push({
      id: 'cash_flow',
      title: 'Flujo de caja',
      message: 'No se pudo cargar el resumen de flujo de caja.',
    })
  }
  if (dto.widgets.safe_to_spend.status === 'error') {
    widgetErrors.push({
      id: 'safe_to_spend',
      title: 'Disponible para gastar',
      message: 'No se pudo calcular el disponible para gastar.',
    })
  }

  return {
    asOf: dto.as_of,
    organization: {
      id: dto.organization.id,
      name: dto.organization.name,
      timezone: dto.organization.timezone,
      currency: dto.organization.currency,
    },
    period: {
      dateFrom: dto.period.date_from,
      dateTo: dto.period.date_to,
      timezone: dto.period.timezone,
    },
    currencies,
    selectedCurrency: dto.selected_currency,
    availableCurrencies: dto.available_currencies ?? currencies.map(c => c.currency),
    metricsStatus: 'ready',
    onboarding,
    attentionItems,
    recentTransactions,
    activityStatus: dto.widgets.activity.status,
    cashFlow,
    upcoming: (dto.widgets.upcoming.data?.items ?? []).map(item => ({
      id: String(item.id),
      dateLabel: String(item.date_label ?? ''),
      description: String(item.description ?? ''),
      amount: item.amount != null ? String(item.amount) : '0.00',
      currency: item.currency ? String(item.currency) : dto.selected_currency,
      status: String(item.status ?? 'normal'),
      to: item.to ? String(item.to) : undefined,
    })),
    upcomingStatus: dto.widgets.upcoming.status,
    financialCommitments: dto.financial_commitments
      ? {
          status: dto.financial_commitments.status,
          activeCount: dto.financial_commitments.active_count,
          overdueCount: dto.financial_commitments.overdue_count,
          totalsByCurrency: (dto.financial_commitments.totals_by_currency ?? []).map(t => ({
            currency: t.currency,
            totalObligations: String(t.total_obligations),
            monthlyPayments: String(t.monthly_payments),
          })),
          nextDue: dto.financial_commitments.next_due
            ? {
                commitmentId: dto.financial_commitments.next_due.commitment_id,
                name: dto.financial_commitments.next_due.name,
                dueInDays: dto.financial_commitments.next_due.due_in_days,
                currency: dto.financial_commitments.next_due.currency ?? undefined,
                amount: dto.financial_commitments.next_due.amount != null
                  ? String(dto.financial_commitments.next_due.amount)
                  : null,
              }
            : null,
          attention: (dto.financial_commitments.attention ?? []).map(a => ({
            commitmentId: a.commitment_id,
            code: a.code,
            message: a.message,
            currency: a.currency ?? undefined,
          })),
          errorCode: dto.financial_commitments.error_code ?? null,
        }
      : null,
    safeToSpend,
    budget: mapModuleWidget(dto.widgets.budget, widgetErrors, 'budget', 'Presupuesto'),
    primaryGoal: enhanceGoalModuleSummary(
      mapModuleWidget(dto.widgets.goal, widgetErrors, 'goal', 'Metas'),
    ),
    debtSummary: mapModuleWidget(dto.widgets.debts, widgetErrors, 'debts', 'Obligaciones'),
    taxSummary: mapModuleWidget(dto.widgets.taxes, widgetErrors, 'taxes', 'Impuestos'),
    widgetErrors,
  }
}

function mapModuleWidget(
  widget: ModuleWidgetDto,
  errors: DashboardWidgetErrorState[],
  id: string,
  title: string,
): DashboardModuleSummary | null {
  if (widget.status === 'error') {
    errors.push({
      id,
      title,
      message: `No se pudo cargar ${title.toLowerCase()}.`,
    })
    return {
      status: 'error',
      title: widget.data?.title ?? title,
      lines: [],
      hint: widget.data?.hint ?? undefined,
      ctaLabel: widget.action?.label,
      ctaTo: widget.action?.to,
      errorCode: widget.error_code ?? null,
    }
  }
  return {
    status: widget.status as DashboardModuleSummary['status'],
    title: widget.data?.title ?? title,
    lines: (widget.data?.lines ?? []).map(line => ({
      label: line.label,
      value: String(line.value),
    })),
    hint: widget.data?.hint ?? undefined,
    ctaLabel: widget.action?.label,
    ctaTo: widget.action?.to,
    errorCode: widget.error_code ?? null,
  }
}

/** Prefer progress-amount lines when the aggregate goal widget is rich; otherwise keep counts. */
export function enhanceGoalModuleSummary(
  module: DashboardModuleSummary | null,
): DashboardModuleSummary | null {
  if (!module) return null
  if (module.status !== 'available' && module.status !== 'ready') return module

  const hasAmountLine = module.lines.some(
    line => /^-?\d+(\.\d+)?$/.test(line.value) && /progreso|objetivo|avance/i.test(line.label),
  )
  if (hasAmountLine) {
    return {
      ...module,
      hint: module.hint ?? 'Meta prioritaria del panorama',
    }
  }

  // Count-only widget — keep as-is (no extra API enrichment).
  return module
}

export function createDashboardRepository(api: ApiClient) {
  return {
    async get(
      organizationId: string,
      options: { period?: string, currency?: string } = {},
    ): Promise<DashboardProjection> {
      const dto = await api.get<DashboardAggregateDto>(
        `/organizations/${organizationId}/dashboard`,
        {
          query: {
            period: options.period ?? 'this_month',
            ...(options.currency ? { currency: options.currency } : {}),
          },
        },
      )
      return mapDashboardAggregate(dto)
    },

    /** Thin adapter kept for callers that still expect the legacy summary shape. */
    async getSummary(organizationId: string) {
      const projection = await this.get(organizationId)
      const slice = projection.currencies.find(c => c.currency === projection.selectedCurrency)
        ?? projection.currencies[0]
      return {
        currency: projection.selectedCurrency,
        netWorth: slice?.netWorth ?? '0.00',
        liquidBalance: slice?.liquidBalance ?? '0.00',
        totalAssets: slice?.totalAssets ?? '0.00',
        totalLiabilities: slice?.totalLiabilities ?? '0.00',
        monthlyIncome: slice?.monthlyIncome ?? '0.00',
        monthlyExpenses: slice?.monthlyExpenses ?? '0.00',
        monthlyNetFlow: slice?.monthlyNetFlow ?? '0.00',
        activeAccounts: 0,
        transactionCount: projection.recentTransactions.length,
        goalsActive: 0,
        goalsCompleted: 0,
        totalDebt: null as string | null,
        debtMinimumPayments: null as string | null,
        activeDebts: 0,
        taxEstimated: null as string | null,
        taxPaid: null as string | null,
        taxBalance: null as string | null,
        taxReserveAssets: null as string | null,
        periodFrom: projection.period.dateFrom,
        periodTo: projection.period.dateTo,
      }
    },
  }
}

export type DashboardRepository = ReturnType<typeof createDashboardRepository>
