import { expect, test } from '@playwright/test'

const ORG_ID = '00000000-0000-4000-8000-000000000001'
const ACCOUNT_ID = '00000000-0000-4000-8000-0000000000c1'
const COMMITMENT_ID = '00000000-0000-4000-8000-0000000000d1'
const USD_ACCOUNT_ID = '00000000-0000-4000-8000-0000000000c2'
const USD_COMMITMENT_ID = '00000000-0000-4000-8000-0000000000d2'

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

async function mockSession(
  page: import('@playwright/test').Page,
  role: 'owner' | 'viewer' = 'owner',
) {
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
            role,
          },
        ],
        total: 1,
      }),
    })
  })
}

function commitmentPayload(overrides: Record<string, unknown> = {}) {
  return {
    id: COMMITMENT_ID,
    organization_id: ORG_ID,
    account_id: ACCOUNT_ID,
    name: 'Tarjeta Nu',
    debt_type: 'credit_card',
    creditor: 'Nu',
    currency: 'MXN',
    priority: 'high',
    interest_rate: '42.00',
    minimum_payment: '1250.00',
    scheduled_payment: null,
    credit_limit: '50000.00',
    original_amount: null,
    maturity_date: null,
    due_day: 20,
    statement_day: 5,
    status: 'active',
    display_status: 'due_soon',
    behavior: 'revolving',
    notes: null,
    version: 1,
    current_balance: '18450.00',
    next_due_date: '2026-08-20',
    days_until_due: 5,
    utilization_percentage: '36.90',
    next_action: {
      type: 'pay_minimum',
      reason_code: 'due_soon',
      amount: '1250.00',
      due_date: '2026-08-20',
    },
    created_at: '2026-07-01T00:00:00Z',
    updated_at: '2026-07-20T00:00:00Z',
    closed_at: null,
    archived_at: null,
    ...overrides,
  }
}

function summaryPayload() {
  return {
    by_currency: [
      {
        currency: 'MXN',
        total_debt: '18450.00',
        total_minimum_payments: '1250.00',
        weighted_average_rate: '42.00',
        active_debt_count: 1,
        highest_interest_debt_id: COMMITMENT_ID,
        highest_interest_rate: '42.00',
      },
      {
        currency: 'USD',
        total_debt: '3200.00',
        total_minimum_payments: '120.00',
        weighted_average_rate: '19.00',
        active_debt_count: 1,
        highest_interest_debt_id: USD_COMMITMENT_ID,
        highest_interest_rate: '19.00',
      },
    ],
    groups: [
      {
        currency: 'MXN',
        total_debt: '18450.00',
        total_minimum_payments: '1250.00',
        weighted_average_rate: '42.00',
        active_debt_count: 1,
        highest_interest_debt_id: COMMITMENT_ID,
        highest_interest_rate: '42.00',
      },
      {
        currency: 'USD',
        total_debt: '3200.00',
        total_minimum_payments: '120.00',
        weighted_average_rate: '19.00',
        active_debt_count: 1,
        highest_interest_debt_id: USD_COMMITMENT_ID,
        highest_interest_rate: '19.00',
      },
    ],
    active_commitments: 2,
    commitments_needing_attention: 1,
    next_due: {
      commitment_id: COMMITMENT_ID,
      name: 'Tarjeta Nu',
      currency: 'MXN',
      due_date: '2026-08-20',
      days_until_due: 5,
      amount: '1250.00',
    },
    attention: [],
  }
}

function strategyPayload() {
  return {
    status: 'ready',
    strategy: 'avalanche',
    generated_at: '2026-07-23T12:00:00Z',
    summary: {
      active_commitments: 2,
      total_balance: '18450.00',
      currency: 'MXN',
    },
    next_action: {
      type: 'pay_priority_debt',
      commitment_id: COMMITMENT_ID,
      reason_code: 'highest_interest',
      amount: '1250.00',
    },
    ranking: [
      {
        commitment_id: COMMITMENT_ID,
        name: 'Tarjeta Nu',
        currency: 'MXN',
        balance: '18450.00',
        interest_rate: '42.00',
        rank: 1,
        reason_code: 'highest_interest',
      },
    ],
    warnings: [],
  }
}

function liabilityAccountsPayload() {
  return {
    items: [
      {
        id: '00000000-0000-4000-8000-0000000000a1',
        organization_id: ORG_ID,
        name: 'HSBC principal',
        account_type: 'checking',
        classification: 'asset',
        currency: 'MXN',
        opening_balance: '50000.00',
        current_balance: '50000.00',
        institution_name: 'HSBC',
        last_four: '1111',
        is_active: true,
        created_at: '2026-07-01T00:00:00Z',
        updated_at: '2026-07-20T00:00:00Z',
        archived_at: null,
      },
      {
        id: ACCOUNT_ID,
        organization_id: ORG_ID,
        name: 'Tarjeta Nu',
        account_type: 'credit_card',
        classification: 'liability',
        currency: 'MXN',
        opening_balance: '-18450.00',
        current_balance: '-18450.00',
        institution_name: 'Nu',
        last_four: '4242',
        is_active: true,
        created_at: '2026-07-01T00:00:00Z',
        updated_at: '2026-07-20T00:00:00Z',
        archived_at: null,
      },
    ],
    total: 2,
  }
}

test.describe('commitments smoke', () => {
  test('list, multi-currency summary, create and pay CTA', async ({ page, context }) => {
    await seedAuth(context)
    await mockSession(page)

    let created = false

    await page.route('**/api/v1/organizations/*/accounts**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(liabilityAccountsPayload()),
      })
    })

    await page.route('**/api/v1/organizations/*/categories**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: '00000000-0000-4000-8000-0000000000ca',
              organization_id: ORG_ID,
              name: 'Transferencias',
              category_type: 'transfer',
              parent_id: null,
              icon: null,
              color: null,
              is_system: true,
              is_active: true,
              children: [],
            },
          ],
          total: 1,
        }),
      })
    })

    await page.route('**/api/v1/organizations/*/debts**', async (route) => {
      const method = route.request().method()
      const url = route.request().url()
      const path = new URL(url).pathname

      if (path.includes('/debts/summary')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(summaryPayload()),
        })
        return
      }

      if (path.includes('/debts/strategy')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(strategyPayload()),
        })
        return
      }

      if (method === 'POST' && /\/debts\/?$/.test(path)) {
        created = true
        const body = route.request().postDataJSON() as Record<string, unknown>
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify(
            commitmentPayload({
              name: body.name,
              debt_type: body.debt_type,
              account_id: body.account_id,
            }),
          ),
        })
        return
      }

      if (method === 'GET' && path.includes('/activity')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ items: [], total: 0 }),
        })
        return
      }

      if (method === 'GET' && path.includes(`/debts/${COMMITMENT_ID}`)) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(
            commitmentPayload({ name: created ? 'Préstamo auto' : 'Tarjeta Nu' }),
          ),
        })
        return
      }

      if (method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: created
              ? []
              : [
                  commitmentPayload(),
                  commitmentPayload({
                    id: USD_COMMITMENT_ID,
                    account_id: USD_ACCOUNT_ID,
                    name: 'Card USD',
                    currency: 'USD',
                    current_balance: '3200.00',
                    display_status: 'active',
                  }),
                ],
            total: created ? 0 : 2,
          }),
        })
        return
      }

      await route.fulfill({ status: 404, body: '{}' })
    })

    await page.goto('/app/commitments')
    await page.waitForLoadState('networkidle')

    await expect(page.getByTestId('commitments-page')).toBeVisible({ timeout: 15_000 })
    await expect(page.getByTestId('page-title')).toHaveText('Obligaciones')
    await expect(page.getByTestId('commitment-card').first()).toBeVisible()
    await expect(page.getByRole('region', { name: 'Listado de obligaciones' }).getByText('Tarjeta Nu')).toBeVisible()
    await expect(page.getByTestId('commitment-summary')).toContainText('MXN')
    await expect(page.getByTestId('commitment-summary')).toContainText('USD')

    await page.getByTestId('commitment-card-pay').first().click()
    await expect(page.getByTestId('quick-transaction-drawer')).toBeVisible({ timeout: 10_000 })
    await expect(page.getByText('Pago de obligación')).toBeVisible()

    await page.goto('/app/commitments/new')
    await page.waitForLoadState('networkidle')
    await expect(page.getByTestId('commitment-new-page')).toBeVisible({ timeout: 10_000 })

    await page.getByTestId('commitment-name').locator('input').fill('Préstamo auto')
    await page.locator('select.ui-select__control').filter({ hasText: 'Tarjeta Nu' }).selectOption(ACCOUNT_ID)
    await page.getByTestId('commitment-create-submit').click()
    await expect(page.getByTestId('commitment-detail-page')).toBeVisible({ timeout: 15_000 })
  })

  test('viewer cannot create commitments', async ({ page, context }) => {
    await seedAuth(context)
    await mockSession(page, 'viewer')

    await page.route('**/api/v1/organizations/*/debts**', async (route) => {
      const path = new URL(route.request().url()).pathname
      if (path.includes('/debts/summary')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(summaryPayload()),
        })
        return
      }
      if (path.includes('/debts/strategy')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(strategyPayload()),
        })
        return
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [commitmentPayload()], total: 1 }),
      })
    })

    await page.goto('/app/commitments')
    await page.waitForLoadState('networkidle')

    await expect(page.getByTestId('commitments-page')).toBeVisible({ timeout: 15_000 })
    await expect(page.getByTestId('commitment-new-button')).toHaveCount(0)
    await expect(page.getByTestId('commitment-card-pay')).toHaveCount(0)
  })

  test('/app/debts redirects to commitments', async ({ page, context }) => {
    await seedAuth(context)
    await mockSession(page)

    await page.route('**/api/v1/organizations/*/debts**', async (route) => {
      const path = new URL(route.request().url()).pathname
      if (path.includes('/debts/summary') || path.includes('/debts/strategy')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [],
            total: 0,
            groups: [],
            active_commitments: 0,
            commitments_needing_attention: 0,
            next_due: null,
            status: 'ready',
            strategy: 'avalanche',
            generated_at: '2026-07-23T12:00:00Z',
            summary: null,
            next_action: null,
            ranking: [],
            warnings: [],
          }),
        })
        return
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      })
    })

    await page.goto('/app/debts')
    await page.waitForURL('**/app/commitments')
    await expect(page.getByTestId('commitments-page')).toBeVisible({ timeout: 15_000 })
  })

  test('shows partial error when summary fails', async ({ page, context }) => {
    await seedAuth(context)
    await mockSession(page)

    await page.route('**/api/v1/organizations/*/debts**', async (route) => {
      const path = new URL(route.request().url()).pathname
      if (path.includes('/debts/summary')) {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: { code: 'internal_error', message: 'boom' } }),
        })
        return
      }
      if (path.includes('/debts/strategy')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(strategyPayload()),
        })
        return
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [commitmentPayload()], total: 1 }),
      })
    })

    await page.goto('/app/commitments')
    await page.waitForLoadState('networkidle')

    await expect(page.getByTestId('commitment-card').first()).toBeVisible({ timeout: 15_000 })
    await expect(page.getByTestId('commitment-summary-error')).toBeVisible()
  })
})
