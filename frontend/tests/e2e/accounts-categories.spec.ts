import { expect, test } from '@playwright/test'

const ORG_ID = '00000000-0000-4000-8000-000000000001'
const ACCOUNT_ID = '00000000-0000-4000-8000-0000000000a1'

async function seedAuth(context: import('@playwright/test').BrowserContext) {
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
}

async function mockSession(page: import('@playwright/test').Page) {
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
}

test.describe('accounts & categories', () => {
  test('accounts list shows mocked account', async ({ page, context }) => {
    await seedAuth(context)
    await mockSession(page)

    await page.route('**/api/v1/organizations/*/accounts**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: ACCOUNT_ID,
              organization_id: ORG_ID,
              name: 'Cuenta principal',
              account_type: 'checking',
              classification: 'asset',
              currency: 'MXN',
              opening_balance: '25000.00',
              current_balance: '25000.00',
              institution_name: 'HSBC',
              last_four: null,
              is_active: true,
              created_at: '2026-07-01T00:00:00Z',
              updated_at: '2026-07-20T00:00:00Z',
              archived_at: null,
            },
          ],
          total: 1,
        }),
      })
    })

    await page.goto('/app/accounts')
    await page.waitForLoadState('networkidle')

    await expect(page.getByTestId('accounts-page')).toBeVisible({ timeout: 15_000 })
    await expect(page.getByTestId('page-title')).toHaveText('Cuentas')
    await expect(page.getByText('Cuenta principal')).toBeVisible()
    await expect(page.getByTestId('account-card')).toBeVisible()
    await expect(page.getByTestId('account-currency-summary')).toBeVisible()
  })

  test('categories page shows tree', async ({ page, context }) => {
    await seedAuth(context)
    await mockSession(page)

    await page.route('**/api/v1/organizations/*/categories**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: '00000000-0000-4000-8000-0000000000c1',
              organization_id: ORG_ID,
              name: 'Comida',
              category_type: 'expense',
              parent_id: null,
              icon: '🍔',
              color: '#0f524e',
              is_system: false,
              is_active: true,
              created_at: '2026-07-01T00:00:00Z',
              updated_at: '2026-07-01T00:00:00Z',
              archived_at: null,
              children: [
                {
                  id: '00000000-0000-4000-8000-0000000000c2',
                  organization_id: ORG_ID,
                  name: 'Restaurantes',
                  category_type: 'expense',
                  parent_id: '00000000-0000-4000-8000-0000000000c1',
                  icon: null,
                  color: null,
                  is_system: false,
                  is_active: true,
                  created_at: '2026-07-01T00:00:00Z',
                  updated_at: '2026-07-01T00:00:00Z',
                  archived_at: null,
                  children: [],
                },
              ],
            },
          ],
          total: 2,
        }),
      })
    })

    await page.goto('/app/categories')
    await page.waitForLoadState('networkidle')

    await expect(page.getByTestId('categories-page')).toBeVisible({ timeout: 15_000 })
    await expect(page.getByTestId('page-title')).toHaveText('Categorías')
    await expect(page.getByTestId('category-tree')).toBeVisible()
    await expect(page.getByText('Comida')).toBeVisible()
    await expect(page.getByText('Restaurantes')).toBeVisible()
  })
})
