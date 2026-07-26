export type DashboardWidgetStatus =
  | 'loading'
  | 'ready'
  | 'empty'
  | 'error'
  | 'not_configured'
  | 'available'
  | 'unavailable'

export type DashboardMetricStatus =
  | 'loading'
  | 'ready'
  | 'empty'
  | 'error'
  | 'not_configured'

export interface DashboardMetric {
  id: string
  label: string
  amount: string | null
  currency: string
  hint?: string
  trendAmount?: string | null
  trendLabel?: string
  status: DashboardMetricStatus
  detailLines?: Array<{ label: string, amount: string }>
  ctaLabel?: string
  ctaTo?: string
}

export interface DashboardAttentionItem {
  id: string
  severity: 'info' | 'warning' | 'critical'
  title: string
  message: string
  amount?: string | null
  currency?: string
  actionLabel: string
  actionTo: string
}

export interface DashboardOnboardingStep {
  id: string
  label: string
  description: string
  completed: boolean
  to: string
}

export interface DashboardOnboarding {
  isVisible: boolean
  completed: boolean
  completedSteps: number
  totalSteps: number
  steps: DashboardOnboardingStep[]
  status: 'ready' | 'empty'
}

export interface DashboardRecentTransaction {
  id: string
  description: string
  transactionType: string
  amount: string
  currency: string
  occurredAt: string
  categoryName: string | null
  accountName: string | null
  status: string
}

export interface DashboardModuleSummary {
  status: DashboardWidgetStatus
  title: string
  lines: Array<{ label: string, value: string }>
  hint?: string
  ctaLabel?: string
  ctaTo?: string
  errorCode?: string | null
}

export interface DashboardCurrencySlice {
  currency: string
  netWorth: string
  liquidBalance: string
  totalAssets: string
  totalLiabilities: string
  monthlyIncome: string
  monthlyExpenses: string
  monthlyNetFlow: string
}

export interface DashboardCashFlowPoint {
  periodStart: string
  income: string
  expenses: string
  netCashFlow: string
}

export interface DashboardCashFlowSummary {
  status: 'ready' | 'empty' | 'error'
  currency: string | null
  income: string | null
  expenses: string | null
  netCashFlow: string | null
  points: DashboardCashFlowPoint[]
  errorCode?: string | null
}

export interface DashboardSafeToSpend {
  status: 'available' | 'not_configured' | 'unavailable' | 'error'
  amount: string | null
  currency: string | null
  fundingGap: string | null
  ctaLabel?: string
  ctaTo?: string
  errorCode?: string | null
}

export interface DashboardWidgetErrorState {
  id: string
  title: string
  message: string
}

export interface DashboardProjection {
  asOf: string
  organization: {
    id: string
    name: string
    timezone: string
    currency: string
  }
  period: {
    dateFrom: string
    dateTo: string
    timezone: string
  }
  currencies: DashboardCurrencySlice[]
  selectedCurrency: string
  availableCurrencies: string[]
  metricsStatus: 'ready'
  onboarding: DashboardOnboarding
  attentionItems: DashboardAttentionItem[]
  recentTransactions: DashboardRecentTransaction[]
  activityStatus: 'ready' | 'empty' | 'error'
  cashFlow: DashboardCashFlowSummary
  upcoming: Array<{
    id: string
    dateLabel: string
    description: string
    amount: string
    currency: string
    status: string
    to?: string
  }>
  upcomingStatus: 'not_configured' | 'empty' | 'ready'
  financialCommitments: {
    status: 'ready' | 'empty' | 'error'
    activeCount: number
    overdueCount: number
    totalsByCurrency: Array<{
      currency: string
      totalObligations: string
      monthlyPayments: string
    }>
    nextDue: {
      commitmentId: string
      name: string
      dueInDays: number
    } | null
    attention: Array<{
      commitmentId: string
      code: string
      message: string
    }>
    errorCode?: string | null
  } | null
  safeToSpend: DashboardSafeToSpend
  budget: DashboardModuleSummary | null
  primaryGoal: DashboardModuleSummary | null
  debtSummary: DashboardModuleSummary | null
  taxSummary: DashboardModuleSummary | null
  widgetErrors: DashboardWidgetErrorState[]
}

export interface DashboardViewModel {
  greeting: string
  subtitle: string
  currency: string
  availableCurrencies: string[]
  asOf: string | null
  metrics: DashboardMetric[]
  attentionItems: DashboardAttentionItem[]
  onboarding: DashboardOnboarding
  recentTransactions: DashboardRecentTransaction[]
  cashFlow: DashboardCashFlowSummary | null
  budget: DashboardModuleSummary | null
  primaryGoal: DashboardModuleSummary | null
  debtSummary: DashboardModuleSummary | null
  taxSummary: DashboardModuleSummary | null
  upcoming: Array<{
    id: string
    dateLabel: string
    description: string
    amount: string
    currency: string
    status: string
    to?: string
  }>
  financialCommitments: DashboardProjection['financialCommitments']
  widgetErrors: DashboardWidgetErrorState[]
}
