import { expect, test } from '@playwright/test'

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
        value: '00000000-0000-4000-8000-000000000001',
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
              id: '00000000-0000-4000-8000-000000000001',
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

    await page.route('**/api/v1/organizations/*/dashboard/summary**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          period: {
            date_from: '2026-07-01',
            date_to: '2026-07-31',
            timezone: 'America/Cancun',
          },
          balances: [
            {
              currency: 'MXN',
              total_assets: '0.00',
              total_liabilities: '0.00',
              net_worth: '0.00',
            },
          ],
          cash_flow: [
            {
              currency: 'MXN',
              income: '0.00',
              expenses: '0.00',
              net_cash_flow: '0.00',
            },
          ],
          account_count: { active: 0, archived: 0 },
          transaction_count: 0,
          goals: { active: 0, completed: 0 },
          debts: null,
          taxes: null,
        }),
      })
    })

    await page.route('**/api/v1/organizations/*/dashboard/recent-transactions**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      })
    })

    await page.route('**/api/v1/organizations/*/planning/summary**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          active_budgets: 0,
          draft_budgets: 0,
          active_cash_plans: 0,
          draft_cash_plans: 0,
          currency: null,
          safe_to_spend: null,
          funding_gap: null,
          primary_cash_plan_id: null,
        }),
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
