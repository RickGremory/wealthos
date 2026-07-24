/**
 * Period helpers and URL query serialization for transaction filters.
 */

export type TransactionTypeFilter =
  | 'all'
  | 'income'
  | 'expense'
  | 'transfer'
  | 'adjustment'

export type TransactionStatusFilter = 'all' | 'posted' | 'voided'

export type QuickPeriod =
  | 'this_month'
  | 'last_month'
  | 'last_30_days'
  | 'this_year'
  | 'custom'
  | 'all'

export interface TransactionFiltersState {
  type: TransactionTypeFilter
  status: TransactionStatusFilter
  accountId: string | null
  categoryId: string | null
  search: string
  period: QuickPeriod
  dateFrom: string | null
  dateTo: string | null
  currency: string | null
}

export function emptyTransactionFilters(): TransactionFiltersState {
  return {
    type: 'all',
    status: 'all',
    accountId: null,
    categoryId: null,
    search: '',
    period: 'this_month',
    dateFrom: null,
    dateTo: null,
    currency: null,
  }
}

function startOfDayIso(date: Date): string {
  const d = new Date(date)
  d.setHours(0, 0, 0, 0)
  return d.toISOString()
}

function endOfDayIso(date: Date): string {
  const d = new Date(date)
  d.setHours(23, 59, 59, 999)
  return d.toISOString()
}

export function resolvePeriodRange(
  period: QuickPeriod,
  customFrom: string | null,
  customTo: string | null,
  now = new Date(),
): { dateFrom: string | null, dateTo: string | null } {
  if (period === 'all') return { dateFrom: null, dateTo: null }
  if (period === 'custom') {
    return {
      dateFrom: customFrom ? startOfDayIso(new Date(customFrom)) : null,
      dateTo: customTo ? endOfDayIso(new Date(customTo)) : null,
    }
  }

  const year = now.getFullYear()
  const month = now.getMonth()

  if (period === 'this_month') {
    return {
      dateFrom: startOfDayIso(new Date(year, month, 1)),
      dateTo: endOfDayIso(now),
    }
  }

  if (period === 'last_month') {
    const from = new Date(year, month - 1, 1)
    const to = new Date(year, month, 0)
    return { dateFrom: startOfDayIso(from), dateTo: endOfDayIso(to) }
  }

  if (period === 'last_30_days') {
    const from = new Date(now)
    from.setDate(from.getDate() - 29)
    return { dateFrom: startOfDayIso(from), dateTo: endOfDayIso(now) }
  }

  if (period === 'this_year') {
    return {
      dateFrom: startOfDayIso(new Date(year, 0, 1)),
      dateTo: endOfDayIso(now),
    }
  }

  return { dateFrom: null, dateTo: null }
}

export function filtersToQuery(
  filters: TransactionFiltersState,
): Record<string, string> {
  const query: Record<string, string> = {}
  if (filters.type !== 'all') query.type = filters.type
  if (filters.status !== 'all') query.status = filters.status
  if (filters.accountId) query.account = filters.accountId
  if (filters.categoryId) query.category = filters.categoryId
  if (filters.search.trim()) query.q = filters.search.trim()
  if (filters.period !== 'this_month') query.period = filters.period
  if (filters.period === 'custom') {
    if (filters.dateFrom) query.from = filters.dateFrom.slice(0, 10)
    if (filters.dateTo) query.to = filters.dateTo.slice(0, 10)
  }
  if (filters.currency) query.currency = filters.currency
  return query
}

export function filtersFromQuery(
  query: Record<string, unknown>,
): TransactionFiltersState {
  const base = emptyTransactionFilters()
  const type = String(query.type ?? '')
  if (['income', 'expense', 'transfer', 'adjustment'].includes(type)) {
    base.type = type as TransactionTypeFilter
  }
  const status = String(query.status ?? '')
  if (status === 'posted' || status === 'voided') {
    base.status = status
  }
  if (typeof query.account === 'string' && query.account) {
    base.accountId = query.account
  }
  if (typeof query.category === 'string' && query.category) {
    base.categoryId = query.category
  }
  if (typeof query.q === 'string') {
    base.search = query.q
  }
  const period = String(query.period ?? '')
  if (['this_month', 'last_month', 'last_30_days', 'this_year', 'custom', 'all'].includes(period)) {
    base.period = period as QuickPeriod
  }
  if (typeof query.from === 'string') base.dateFrom = query.from
  if (typeof query.to === 'string') base.dateTo = query.to
  if (typeof query.currency === 'string') base.currency = query.currency
  return base
}
