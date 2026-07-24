import { defineConfig, devices } from '@playwright/test'

const E2E_PORT = 3010
const E2E_ORIGIN = `http://localhost:${E2E_PORT}`

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'list',
  use: {
    baseURL: E2E_ORIGIN,
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    // Dedicated port + SPA mode so Playwright route mocks work (SSR bypasses them).
    command: `NUXT_IGNORE_LOCK=1 NUXT_SSR=false npm run dev -- --host localhost --port ${E2E_PORT}`,
    url: E2E_ORIGIN,
    reuseExistingServer: false,
    timeout: 120_000,
    env: {
      NUXT_SSR: 'false',
      NUXT_IGNORE_LOCK: '1',
    },
  },
})
