import type { ApiClient } from '~/lib/api/types'
import type { DashboardRecentTransaction } from '~/types/dashboard'

interface NamedRefDto {
  id: string
  name: string
}

interface CurrencyBalanceDto {
  currency: string
  total_assets: string
  total_liabilities: string
  net_worth: string
}

interface CurrencyCashFlowDto {
  currency: string
  income: string
  expenses: string
  net_cash_flow: string
}

interface DashboardSummaryDto {
  period: {
    date_from: string
    date_to: string
    timezone: string
  }
  balances: CurrencyBalanceDto[]
  cash_flow: CurrencyCashFlowDto[]
  account_count: {
    active: number
    archived: number
  }
  transaction_count: number
  goals?: {
    active: number
    completed: number
  } | null
  debts?: {
    total_debt: string
    total_minimum_payments: string
    active_count: number
  } | null
  taxes?: {
    estimated_tax: string
    paid: string
    balance: string
    cash_like_assets: string
    available_after_tax: string
  } | null
}

interface RecentTransactionDto {
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

interface RecentTransactionsDto {
  items: RecentTransactionDto[]
  total: number
}

export interface DashboardSummaryData {
  currency: string
  netWorth: string
  totalAssets: string
  totalLiabilities: string
  monthlyIncome: string
  monthlyExpenses: string
  monthlyNetFlow: string
  activeAccounts: number
  transactionCount: number
  goalsActive: number
  goalsCompleted: number
  totalDebt: string | null
  debtMinimumPayments: string | null
  activeDebts: number
  taxEstimated: string | null
  taxPaid: string | null
  taxBalance: string | null
  taxReserveAssets: string | null
  periodFrom: string
  periodTo: string
}

export function createDashboardRepository(api: ApiClient) {
  return {
    async getSummary(organizationId: string): Promise<DashboardSummaryData> {
      const dto = await api.get<DashboardSummaryDto>(
        `/organizations/${organizationId}/dashboard/summary`,
        { query: { period: 'this_month' } },
      )

      const balance = dto.balances[0]
      const flow = dto.cash_flow[0]
      const currency = balance?.currency ?? flow?.currency ?? 'MXN'

      return {
        currency,
        netWorth: String(balance?.net_worth ?? '0.00'),
        totalAssets: String(balance?.total_assets ?? '0.00'),
        totalLiabilities: String(balance?.total_liabilities ?? '0.00'),
        monthlyIncome: String(flow?.income ?? '0.00'),
        monthlyExpenses: String(flow?.expenses ?? '0.00'),
        monthlyNetFlow: String(flow?.net_cash_flow ?? '0.00'),
        activeAccounts: dto.account_count.active,
        transactionCount: dto.transaction_count,
        goalsActive: dto.goals?.active ?? 0,
        goalsCompleted: dto.goals?.completed ?? 0,
        totalDebt: dto.debts ? String(dto.debts.total_debt) : null,
        debtMinimumPayments: dto.debts ? String(dto.debts.total_minimum_payments) : null,
        activeDebts: dto.debts?.active_count ?? 0,
        taxEstimated: dto.taxes ? String(dto.taxes.estimated_tax) : null,
        taxPaid: dto.taxes ? String(dto.taxes.paid) : null,
        taxBalance: dto.taxes ? String(dto.taxes.balance) : null,
        taxReserveAssets: dto.taxes ? String(dto.taxes.cash_like_assets) : null,
        periodFrom: dto.period.date_from,
        periodTo: dto.period.date_to,
      }
    },

    async getRecentTransactions(
      organizationId: string,
      limit = 8,
    ): Promise<DashboardRecentTransaction[]> {
      const dto = await api.get<RecentTransactionsDto>(
        `/organizations/${organizationId}/dashboard/recent-transactions`,
        { query: { limit } },
      )
      return (dto.items ?? []).map(item => ({
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
    },

    async getSafeToSpend(organizationId: string): Promise<{
      currency: string | null
      safeToSpend: string | null
      configured: boolean
    } | null> {
      try {
        const dto = await api.get<{
          currency: string | null
          safe_to_spend: string | null
          active_budgets: number
          active_cash_plans: number
        }>(`/organizations/${organizationId}/planning/summary`)
        return {
          currency: dto.currency,
          safeToSpend: dto.safe_to_spend != null ? String(dto.safe_to_spend) : null,
          configured: dto.active_cash_plans > 0 || dto.active_budgets > 0,
        }
      } catch {
        return null
      }
    },
  }
}

export type DashboardRepository = ReturnType<typeof createDashboardRepository>
