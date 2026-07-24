export type DashboardWidgetStatus =
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
  status: DashboardWidgetStatus
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
  completed: boolean
  completedSteps: number
  totalSteps: number
  steps: DashboardOnboardingStep[]
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
}

export interface DashboardViewModel {
  greeting: string
  subtitle: string
  currency: string
  asOf: string | null
  metrics: DashboardMetric[]
  attentionItems: DashboardAttentionItem[]
  onboarding: DashboardOnboarding
  recentTransactions: DashboardRecentTransaction[]
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
  }>
}
