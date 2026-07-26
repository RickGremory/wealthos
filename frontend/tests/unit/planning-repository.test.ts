import { describe, expect, it, vi } from 'vitest'
import { createPlanningRepository } from '~/repositories/planning.repository'
import type { ApiClient } from '~/lib/api/types'

describe('planning.repository paths', () => {
  it('does not double-prefix /api/v1', async () => {
    const get = vi.fn().mockResolvedValue({
      organization_id: 'org-1',
      currency: 'MXN',
      horizon: '30_days',
      period_start: '2026-08-01T00:00:00Z',
      period_end: '2026-08-31T00:00:00Z',
      calculated_at: '2026-08-01T00:00:00Z',
      status: 'healthy',
      confidence: 'high',
      confidence_reasons: [],
      current_available_cash: '100.00',
      expected_income: '0.00',
      committed_outflows: '0.00',
      protected_funds: '0.00',
      safe_to_spend: '100.00',
      projected_ending_balance: '100.00',
      minimum_projected_balance: '100.00',
      lowest_balance_at: null,
      cash_deficit: null,
      reserve_shortfall: null,
      timeline: [],
      breakdown: [],
      alerts: [],
    })
    const api = { get } as unknown as ApiClient
    const repo = createPlanningRepository(api)
    await repo.getProjection('org-1', { currency: 'MXN', horizon: '30_days' })
    expect(get).toHaveBeenCalledWith(
      '/organizations/org-1/planning/projection',
      expect.objectContaining({
        query: { currency: 'MXN', horizon: '30_days' },
      }),
    )
  })
})
