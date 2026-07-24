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

    await page.goto('/app/dashboard')
    await page.waitForLoadState('networkidle')

    await expect(page.getByTestId('page-title')).toHaveText('Dashboard', { timeout: 15_000 })

    const logout = page.getByTestId('logout-button')
    await expect(logout).toBeVisible()
    await logout.click()
    await expect(page).toHaveURL(/\/login/)
  })
})
