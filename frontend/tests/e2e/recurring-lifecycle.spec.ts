import { expect, test } from '@playwright/test'

const ORG_ID = '00000000-0000-4000-8000-000000000001'
const RULE_ID = '00000000-0000-4000-8000-0000000000r1'
const ACCOUNT_ID = '00000000-0000-4000-8000-0000000000a1'
const CATEGORY_ID = '00000000-0000-4000-8000-0000000000c1'

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

function ruleDetail(overrides: Record<string, unknown> = {}) {
  return {
    id: RULE_ID,
    name: 'Internet',
    direction: 'outflow',
    amount: '800.00',
    currency: 'MXN',
    status: 'active',
    source_type: 'manual',
    is_managed_externally: false,
    frequency: 'monthly',
    interval: 1,
    schedule_label: 'Cada mes el día 15',
    version: 1,
    next_occurrence: {
      occurrence_key: `recurring:${RULE_ID}:occurrence:2026-08-15`,
      recurring_rule_id: RULE_ID,
      original_expected_on: '2026-08-15',
      expected_on: '2026-08-15',
      expected_at: '2026-08-15T12:00:00Z',
      direction: 'outflow',
      base_amount: '800.00',
      expected_amount: '800.00',
      currency: 'MXN',
      certainty: 'expected',
      status: 'open',
      is_exception: false,
      exception_type: null,
      name: 'Internet',
      account_id: ACCOUNT_ID,
      destination_account_id: null,
      category_id: CATEGORY_ID,
      actual_amount: null,
      variance_amount: null,
      can_confirm: true,
      can_skip: true,
      can_reschedule: true,
    },
    upcoming_occurrences: [],
    current_version: {
      id: '00000000-0000-4000-8000-0000000000v1',
      effective_from: '2026-07-15',
      effective_until: null,
      name: 'Internet',
      direction: 'outflow',
      amount: '800.00',
      currency: 'MXN',
      frequency: 'monthly',
      interval: 1,
      day_of_month: 15,
      end_of_month: false,
      days_of_week: [],
      month_of_year: null,
      invalid_date_policy: 'clip',
      starts_on: '2026-07-15',
      ends_on: null,
      grace_period_days: 0,
      amount_strategy: 'fixed',
      certainty: 'expected',
      settlement_mode: 'exact',
      account_id: ACCOUNT_ID,
      destination_account_id: null,
      category_id: CATEGORY_ID,
      notes: null,
    },
    pauses: [],
    exceptions: [],
    ...overrides,
  }
}

async function mockRecurringApis(page: import('@playwright/test').Page) {
  await page.route(`**/api/v1/organizations/${ORG_ID}/accounts**`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [
          {
            id: ACCOUNT_ID,
            organization_id: ORG_ID,
            name: 'Cheques',
            account_type: 'checking',
            classification: 'asset',
            currency: 'MXN',
            current_balance: '5000.00',
            is_archived: false,
          },
        ],
        total: 1,
      }),
    })
  })

  await page.route(`**/api/v1/organizations/${ORG_ID}/categories**`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: CATEGORY_ID,
          name: 'Servicios',
          type: 'expense',
          is_system: false,
          is_archived: false,
          children: [],
        },
      ]),
    })
  })

  await page.route(`**/api/v1/organizations/${ORG_ID}/recurring/preview**`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        dates: ['2026-08-15', '2026-09-15', '2026-10-15'],
        occurrences: [],
      }),
    })
  })

  await page.route(`**/api/v1/organizations/${ORG_ID}/recurring/occurrences**`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          occurrence_key: `recurring:${RULE_ID}:occurrence:2026-08-15`,
          recurring_rule_id: RULE_ID,
          original_expected_on: '2026-08-15',
          expected_on: '2026-08-15',
          expected_at: '2026-08-15T12:00:00Z',
          direction: 'outflow',
          base_amount: '800.00',
          expected_amount: '800.00',
          currency: 'MXN',
          certainty: 'expected',
          status: 'open',
          is_exception: false,
          exception_type: null,
          name: 'Internet',
          account_id: ACCOUNT_ID,
          destination_account_id: null,
          category_id: CATEGORY_ID,
          actual_amount: null,
          variance_amount: null,
          can_confirm: true,
          can_skip: true,
          can_reschedule: true,
        },
      ]),
    })
  })

  await page.route(`**/api/v1/organizations/${ORG_ID}/recurring/${RULE_ID}**`, async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(ruleDetail()),
      })
      return
    }
    await route.continue()
  })

  await page.route(`**/api/v1/organizations/${ORG_ID}/recurring**`, async (route) => {
    const method = route.request().method()
    const url = route.request().url()
    if (url.includes('/preview') || url.includes('/occurrences') || url.includes(`/${RULE_ID}`)) {
      await route.fallback()
      return
    }
    if (method === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: RULE_ID,
            name: 'Internet',
            direction: 'outflow',
            amount: '800.00',
            currency: 'MXN',
            status: 'active',
            source_type: 'manual',
            is_managed_externally: false,
            frequency: 'monthly',
            interval: 1,
            schedule_label: 'Cada mes el día 15',
            version: 1,
            next_occurrence: ruleDetail().next_occurrence,
          },
        ]),
      })
      return
    }
    if (method === 'POST') {
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify(ruleDetail()),
      })
      return
    }
    await route.continue()
  })
}

test.describe('Recurring lifecycle smoke', () => {
  test('owner can open list, create form, and detail', async ({ page, context }) => {
    await seedAuth(context)
    await mockSession(page, 'owner')
    await mockRecurringApis(page)

    await page.goto('/app/recurring')
    await expect(page.getByTestId('recurring-page')).toBeVisible()
    await expect(page.getByTestId('recurring-new-button')).toBeVisible()
    await expect(page.getByText('Internet')).toBeVisible()

    await page.getByTestId('recurring-new-button').click()
    await expect(page.getByTestId('recurring-new-page')).toBeVisible()
    await expect(page.getByTestId('recurring-name')).toBeVisible()

    await page.goto(`/app/recurring/${RULE_ID}`)
    await expect(page.getByTestId('recurring-detail-page')).toBeVisible()
    await expect(page.getByText('Internet').first()).toBeVisible()
  })

  test('viewer cannot create recurring rules', async ({ page, context }) => {
    await seedAuth(context)
    await mockSession(page, 'viewer')
    await mockRecurringApis(page)

    await page.goto('/app/recurring')
    await expect(page.getByTestId('recurring-page')).toBeVisible()
    await expect(page.getByTestId('recurring-new-button')).toHaveCount(0)
  })
})
