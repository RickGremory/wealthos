import { expect, test } from '@playwright/test'

const ORG_ID = '00000000-0000-4000-8000-000000000001'

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

test('Historia page renders timeline feed', async ({ page, context }) => {
  await seedAuth(context)

  await page.route('**/api/v1/**', async (route) => {
    const url = new URL(route.request().url())
    const path = url.pathname
    const method = route.request().method()

    if (method === 'GET' && path.endsWith('/me')) {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: '00000000-0000-4000-8000-000000000099',
          email: 'e2e@wealthos.test',
          display_name: 'E2E',
        }),
      })
    }

    if (method === 'GET' && path.includes('/me/organizations')) {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [{
            id: ORG_ID,
            name: 'E2E Org',
            currency: 'MXN',
            timezone: 'America/Mexico_City',
            role: 'owner',
          }],
        }),
      })
    }

    if (method === 'GET' && path.includes('/timeline')) {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: '00000000-0000-4000-8000-0000000000t1',
              organization_id: ORG_ID,
              occurred_at: '2026-07-25T12:00:00Z',
              source_type: 'transaction',
              event_type: 'transaction.income_posted',
              importance: 'high',
              title: 'Ingreso registrado',
              description: 'Nomina',
              resource_type: 'transaction',
              resource_id: '00000000-0000-4000-8000-0000000000a1',
              currency: 'MXN',
              amount: '10000.00',
              metadata: {},
            },
          ],
          next_cursor: null,
          limit: 40,
        }),
      })
    }

    return route.fulfill({ status: 200, contentType: 'application/json', body: '{}' })
  })

  await page.goto('/app/timeline')
  await expect(page.getByRole('heading', { name: 'Historia' })).toBeVisible()
  await expect(page.getByText('Ingreso registrado')).toBeVisible()
  await expect(page.getByText('Nomina')).toBeVisible()
})
