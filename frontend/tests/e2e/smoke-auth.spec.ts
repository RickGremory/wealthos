import { expect, test } from '@playwright/test'

const ORG_ID = '00000000-0000-4000-8000-000000000001'

test.describe('smoke auth shell', () => {
  test('shows app shell when cookie is set and skips real API', async ({ page, context }) => {
    await context.addCookies([
      {
        name: 'wealthos_access_token',
        value: 'e2e-fake-token',
        domain: 'localhost',
        path: '/',
      },
      {
        name: 'wealthos_organization_id',
        value: ORG_ID,
        domain: 'localhost',
        path: '/',
      },
      {
        name: 'wealthos_onboarding_progress',
        value: JSON.stringify({
          [ORG_ID]: {
            hasPreferences: true,
            preferences: ['spend_control'],
            skippedAccount: true,
            markedComplete: true,
          },
        }),
        domain: 'localhost',
        path: '/',
      },
    ])

    await page.route('**/api/v1/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: '00000000-0000-4000-8000-000000000010',
          email: 'e2e@wealthos.test',
          display_name: 'E2E User',
          is_active: true,
          created_at: '2026-01-01T00:00:00Z',
          updated_at: '2026-01-01T00:00:00Z',
        }),
      })
    })

    await page.route('**/api/v1/me/organizations', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: ORG_ID,
              name: 'Org E2E',
              slug: 'org-e2e',
              currency: 'MXN',
              timezone: 'America/Cancun',
              locale: 'es-MX',
              role: 'owner',
            },
          ],
          total: 1,
        }),
      })
    })

    await page.route('**/api/v1/organizations/*/accounts**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      })
    })

    await page.route('**/api/v1/organizations/*/dashboard**', async (route) => {
      const url = route.request().url()
      // Match exact aggregate endpoint; keep subpaths from falling through if needed.
      if (/\/dashboard(\?|$)/.test(url) || /\/dashboard$/.test(url.split('?')[0] ?? '')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            as_of: '2026-07-24T20:00:00Z',
            organization: {
              id: ORG_ID,
              name: 'Org E2E',
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
                net_worth: '0.00',
                liquid_balance: '0.00',
                total_assets: '0.00',
                total_liabilities: '0.00',
                monthly_income: '0.00',
                monthly_expenses: '0.00',
                monthly_net_flow: '0.00',
              },
            ],
            selected_currency: 'MXN',
            available_currencies: ['MXN'],
            widgets: {
              metrics: { status: 'ready' },
              onboarding: {
                status: 'ready',
                data: {
                  is_visible: true,
                  completed: false,
                  completed_steps: 0,
                  total_steps: 3,
                  steps: [
                    {
                      id: 'create_account',
                      label: 'Crea tu primera cuenta',
                      description: 'Checking, ahorro o efectivo para empezar.',
                      completed: false,
                      to: '/app/accounts',
                    },
                    {
                      id: 'record_income',
                      label: 'Registra un ingreso',
                      description: 'Un cobro reciente basta para activar el flujo.',
                      completed: false,
                      to: '/app/transactions',
                    },
                    {
                      id: 'record_expense',
                      label: 'Registra un gasto',
                      description: 'Empieza a ver en qué se va el dinero.',
                      completed: false,
                      to: '/app/transactions',
                    },
                    {
                      id: 'create_budget',
                      label: 'Crea un presupuesto',
                      description: 'Define cuánto puedes gastar este mes.',
                      completed: false,
                      to: '/app/planning',
                    },
                  ],
                },
              },
              attention: { status: 'empty', data: { items: [] } },
              activity: { status: 'empty', data: { items: [] } },
              cash_flow: { status: 'empty', data: null },
              upcoming: { status: 'not_configured', data: { items: [] } },
              safe_to_spend: {
                status: 'not_configured',
                data: null,
                action: { label: 'Configura tu flujo de caja', to: '/app/planning' },
              },
              budget: {
                status: 'not_configured',
                data: {
                  title: 'Presupuesto del mes',
                  lines: [],
                  hint: 'Crea un presupuesto',
                },
                action: { label: 'Crear presupuesto', to: '/app/planning' },
              },
              goal: {
                status: 'not_configured',
                data: { title: 'Metas', lines: [], hint: 'Define una meta' },
                action: { label: 'Crear meta', to: '/app/goals' },
              },
              debts: {
                status: 'not_configured',
                data: { title: 'Deudas', lines: [], hint: 'Registra pasivos' },
                action: { label: 'Agregar deuda', to: '/app/debts' },
              },
              taxes: {
                status: 'not_configured',
                data: { title: 'Impuestos', lines: [], hint: 'Configura perfil fiscal' },
                action: { label: 'Configurar impuestos', to: '/app/taxes' },
              },
            },
          }),
        })
        return
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({}),
      })
    })

    await page.goto('/app/dashboard')
    await page.waitForLoadState('networkidle')

    await expect(page.getByTestId('dashboard-page')).toBeVisible({ timeout: 15_000 })
    await expect(page.getByTestId('page-title')).toBeVisible()
    await expect(page.getByText('Comienza a construir tu panorama financiero')).toBeVisible()
    await expect(page.getByTestId('new-transaction-button')).toBeVisible()

    const logout = page.getByTestId('logout-button')
    await expect(logout).toBeVisible()
    await logout.click()
    await expect(page).toHaveURL(/\/login/)
  })
})
