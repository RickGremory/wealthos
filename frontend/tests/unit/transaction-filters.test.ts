import { describe, expect, it } from 'vitest'
import {
  emptyTransactionFilters,
  filtersFromQuery,
  filtersToQuery,
  hasActiveFilters,
  resolvePeriodRange,
} from '../../utils/transaction-filters'

describe('transaction-filters', () => {
  it('starts with this_month defaults', () => {
    const f = emptyTransactionFilters()
    expect(f.type).toBe('all')
    expect(f.status).toBe('all')
    expect(f.period).toBe('this_month')
  })

  it('resolves this_month range', () => {
    const now = new Date(2026, 6, 24, 15, 0, 0) // Jul 24
    const range = resolvePeriodRange('this_month', null, null, now)
    expect(range.dateFrom).toContain('2026-07-01')
    expect(range.dateTo).toBeTruthy()
  })

  it('resolves last_month', () => {
    const now = new Date(2026, 6, 24)
    const range = resolvePeriodRange('last_month', null, null, now)
    expect(range.dateFrom).toBeTruthy()
    expect(range.dateTo).toBeTruthy()
    // Local June 1 → ISO may shift by TZ; assert month boundary via Date parts
    const from = new Date(range.dateFrom!)
    const to = new Date(range.dateTo!)
    expect(from.getMonth()).toBe(5) // June
    expect(to.getMonth()).toBe(5)
    expect(from.getDate()).toBe(1)
  })

  it('round-trips query serialization', () => {
    const filters = emptyTransactionFilters()
    filters.type = 'expense'
    filters.status = 'posted'
    filters.accountId = 'acc-1'
    filters.search = 'cafe'
    filters.period = 'last_30_days'
    const query = filtersToQuery(filters)
    expect(query).toEqual({
      type: 'expense',
      status: 'posted',
      account: 'acc-1',
      q: 'cafe',
      period: 'last_30_days',
    })
    const back = filtersFromQuery(query)
    expect(back.type).toBe('expense')
    expect(back.accountId).toBe('acc-1')
    expect(back.search).toBe('cafe')
    expect(back.period).toBe('last_30_days')
  })

  it('keeps this_month out of query', () => {
    expect(filtersToQuery(emptyTransactionFilters())).toEqual({})
  })

  it('detects active filters', () => {
    expect(hasActiveFilters(emptyTransactionFilters())).toBe(false)
    expect(hasActiveFilters({ ...emptyTransactionFilters(), type: 'income' })).toBe(true)
    expect(hasActiveFilters({ ...emptyTransactionFilters(), period: 'all' })).toBe(true)
  })
})
