import { expect, test } from '@playwright/test'

const ORG_ID = '00000000-0000-4000-8000-000000000001'
const ACCOUNT_ID = '00000000-0000-4000-8000-0000000000a1'
const GOAL_ID = '00000000-0000-4000-8000-0000000000g1'

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

function goalPayload(overrides: Record<string, unknown> = {}) {
  return {
    id: GOAL_ID,
    organization_id: ORG_ID,
    name: 'Fondo de emergencia',
    target_amount: '50000.00',
    currency: 'MXN',
    target_date: '2026-12-31',
    strategy: 'manual',
    linked_account_ids: [],
    status: 'active',
    current_amount: '10000.00',
    remaining_amount: '40000.00',
    completion_percentage: '20.00',
    estimated_completion_date: null,
    created_at: '2026-07-01T00:00:00Z',
    updated_at: '2026-07-20T00:00:00Z',
    completed_at: null,
    archived_at: null,
    ...overrides,
  }
}

function accountsPayload() {
  return {
    items: [
      {
        id: ACCOUNT_ID,
        organization_id: ORG_ID,
        name: 'Ahorro MXN',
        account_type: 'savings',
        classification: 'asset',
        currency: 'MXN',
        opening_balance: '10000.00',
        current_balance: '10000.00',
        institution_name: null,
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

test.describe('goals smoke', () => {
  test('list shows mocked goal and create flow works', async ({ page, context }) => {
    await seedAuth(context)
    await mockSession(page)

    let created = false

    await page.route('**/api/v1/organizations/*/accounts**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(accountsPayload()),
      })
    })

    await page.route('**/api/v1/organizations/*/goals**', async (route) => {
      const method = route.request().method()
      const url = route.request().url()

      if (method === 'POST' && url.endsWith('/goals')) {
        created = true
        const body = route.request().postDataJSON() as Record<string, unknown>
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify(
            goalPayload({
              name: body.name,
              target_amount: String(body.target_amount),
              strategy: body.strategy,
              current_amount: '0.00',
              remaining_amount: String(body.target_amount),
              completion_percentage: '0',
            }),
          ),
        })
        return
      }

      if (method === 'GET' && url.includes(`/goals/${GOAL_ID}`)) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(goalPayload({ name: created ? 'Viaje a Oaxaca' : 'Fondo de emergencia' })),
        })
        return
      }

      if (method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: created ? [] : [goalPayload()],
            total: created ? 0 : 1,
          }),
        })
        return
      }

      await route.fulfill({ status: 404, body: '{}' })
    })

    await page.goto('/app/goals')
    await page.waitForLoadState('networkidle')

    await expect(page.getByTestId('goals-page')).toBeVisible({ timeout: 15_000 })
    await expect(page.getByTestId('page-title')).toHaveText('Metas')
    await expect(page.getByTestId('goal-card')).toBeVisible()
    await expect(page.getByText('Fondo de emergencia')).toBeVisible()

    await page.getByTestId('goal-new-button').click()
    await expect(page.getByTestId('goal-new-page')).toBeVisible({ timeout: 10_000 })

    await page.getByLabel('Nombre').fill('Viaje a Oaxaca')
    const money = page.getByTestId('money-input').locator('input')
    await money.fill('15000')
    await money.blur()

    await page.getByTestId('goal-create-submit').click()
    await expect(page.getByTestId('goal-detail-page')).toBeVisible({ timeout: 15_000 })
    await expect(page.getByText('Viaje a Oaxaca')).toBeVisible()
  })
})
