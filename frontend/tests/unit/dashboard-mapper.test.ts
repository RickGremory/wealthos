import { describe, expect, it } from 'vitest'
import { mapDashboardAggregate } from '../../repositories/dashboard.repository'

function baseDto(overrides: Record<string, unknown> = {}) {
  return {
    as_of: '2026-07-24T20:00:00Z',
    organization: {
      id: 'org-1',
      name: 'Demo',
      timezone: 'America/Cancun',
      currency: 'MXN',
    },
    period: {
      date_from: '2026-07-01',
      date_to: '2026-07-31',
      timezone: 'America/Cancun',
    },
    currencies: [
      {
        currency: 'MXN',
        net_worth: '21000.00',
        liquid_balance: '15000.00',
        total_assets: '26000.00',
        total_liabilities: '5000.00',
        monthly_income: '10000.00',
        monthly_expenses: '4000.00',
        monthly_net_flow: '6000.00',
      },
    ],
    selected_currency: 'MXN',
    available_currencies: ['MXN'],
    widgets: {
      metrics: { status: 'ready' as const },
      onboarding: {
        status: 'ready' as const,
        data: {
          is_visible: true,
          completed: false,
          completed_steps: 1,
          total_steps: 3,
          steps: [],
        },
      },
      attention: { status: 'empty' as const, data: { items: [] } },
      activity: { status: 'empty' as const, data: { items: [] } },
      cash_flow: { status: 'empty' as const, data: null },
      upcoming: { status: 'not_configured' as const, data: { items: [] } },
      safe_to_spend: {
        status: 'not_configured' as const,
        data: null,
        action: { label: 'Configura tu flujo de caja', to: '/app/planning' },
      },
      budget: {
        status: 'not_configured',
        data: { title: 'Presupuesto del mes', lines: [], hint: 'Crea uno' },
        action: { label: 'Crear', to: '/app/planning' },
      },
      goal: {
        status: 'not_configured',
        data: { title: 'Metas', lines: [] },
        action: null,
      },
      debts: {
        status: 'not_configured',
        data: { title: 'Deudas', lines: [] },
        action: null,
      },
      taxes: {
        status: 'not_configured',
        data: { title: 'Impuestos', lines: [] },
        action: null,
      },
    },
    ...overrides,
  }
}

describe('mapDashboardAggregate', () => {
  it('maps liquid from liquid_balance, not total_assets', () => {
    const projection = mapDashboardAggregate(baseDto())
    expect(projection.currencies[0].liquidBalance).toBe('15000.00')
    expect(projection.currencies[0].totalAssets).toBe('26000.00')
    expect(projection.currencies[0].liquidBalance).not.toBe(
      projection.currencies[0].totalAssets,
    )
  })

  it('keeps safe_to_spend null when not_configured', () => {
    const projection = mapDashboardAggregate(baseDto())
    expect(projection.safeToSpend.status).toBe('not_configured')
    expect(projection.safeToSpend.amount).toBeNull()
  })

  it('maps available safe_to_spend amount', () => {
    const projection = mapDashboardAggregate(
      baseDto({
        widgets: {
          ...baseDto().widgets,
          safe_to_spend: {
            status: 'available',
            data: {
              currency: 'MXN',
              safe_to_spend: '3200.50',
              funding_gap: null,
            },
            action: { label: 'Ver Planning', to: '/app/planning' },
          },
        },
      }),
    )
    expect(projection.safeToSpend.status).toBe('available')
    expect(projection.safeToSpend.amount).toBe('3200.50')
  })
})
