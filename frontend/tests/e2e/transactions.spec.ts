import { expect, test } from '@playwright/test'

const ORG_ID = '00000000-0000-4000-8000-000000000001'
const ACCOUNT_ID = '00000000-0000-4000-8000-0000000000a1'
const TX_ID = '00000000-0000-4000-8000-0000000000t1'
const CAT_ID = '00000000-0000-4000-8000-0000000000c1'

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

function accountPayload() {
  return {
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
  }
}

function categoryPayload() {
  return {
    items: [
      {
        id: CAT_ID,
        organization_id: ORG_ID,
        name: 'Comida',
        category_type: 'expense',
        parent_id: null,
        icon: null,
        color: null,
        is_system: false,
        is_active: true,
        children: [],
      },
    ],
    total: 1,
  }
}

function transactionItem() {
  return {
    id: TX_ID,
    organization_id: ORG_ID,
    transaction_type: 'expense',
    description: 'Café de la mañana',
    category_id: CAT_ID,
    occurred_at: '2026-07-20T12:00:00Z',
    notes: null,
    status: 'posted',
    entries: [
      {
        id: '00000000-0000-4000-8000-0000000000e1',
        account_id: ACCOUNT_ID,
        amount: '-45.00',
        currency: 'MXN',
      },
    ],
    created_by_user_id: '00000000-0000-4000-8000-000000000010',
    updated_by_user_id: '00000000-0000-4000-8000-000000000010',
    voided_by_user_id: null,
    created_at: '2026-07-20T12:00:00Z',
    updated_at: '2026-07-20T12:00:00Z',
    voided_at: null,
    amount: '45.00',
  }
}

test.describe('transactions', () => {
  test('list page shows mocked transaction', async ({ page, context }) => {
    await seedAuth(context)
    await mockSession(page)

    await page.route('**/api/v1/organizations/*/accounts**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(accountPayload()),
      })
    })

    await page.route('**/api/v1/organizations/*/categories**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(categoryPayload()),
      })
    })

    await page.route('**/api/v1/organizations/*/transactions**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [transactionItem()],
          total: 1,
          limit: 40,
          offset: 0,
        }),
      })
    })

    await page.goto('/app/transactions')
    await page.waitForLoadState('networkidle')

    await expect(page.getByTestId('transactions-page')).toBeVisible({ timeout: 15_000 })
    await expect(page.getByTestId('page-title')).toHaveText('Movimientos')
    await expect(page.getByRole('link', { name: 'Café de la mañana' })).toBeVisible()
  })

  test('topbar opens quick transaction drawer', async ({ page, context }) => {
    await seedAuth(context)
    await mockSession(page)

    await page.route('**/api/v1/organizations/*/accounts**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(accountPayload()),
      })
    })

    await page.route('**/api/v1/organizations/*/categories**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(categoryPayload()),
      })
    })

    await page.route('**/api/v1/organizations/*/transactions**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0, limit: 40, offset: 0 }),
      })
    })

    // dashboard may be hit via redirects; keep soft
    await page.route('**/api/v1/organizations/*/dashboard**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({}),
      })
    })

    await page.goto('/app/transactions')
    await page.waitForLoadState('networkidle')

    await page.getByTestId('new-transaction-button').click()
    await expect(page.getByTestId('quick-transaction-drawer')).toBeVisible({ timeout: 10_000 })
    await expect(page.getByTestId('transaction-form')).toBeVisible()
    await expect(page.getByTestId('transaction-type-selector')).toBeVisible()
  })
})
