import type { ApiClient } from '~/lib/api/types'
import { createAccountsRepository } from '~/repositories/accounts.repository'
import type { OnboardingOrgProgress } from '~/stores/onboarding'

export interface ComposedOnboardingProgress extends OnboardingOrgProgress {
  hasAccount: boolean
}

/**
 * Composes onboarding progress from the cookie-backed store snapshot
 * plus live account presence for the organization.
 */
export function createOnboardingRepository(api: ApiClient) {
  const accounts = createAccountsRepository(api)

  return {
    async getProgress(
      organizationId: string,
      stored: OnboardingOrgProgress,
    ): Promise<ComposedOnboardingProgress> {
      const list = await accounts.list(organizationId)
      return {
        ...stored,
        hasAccount: list.length > 0,
      }
    },

    async hasAccount(organizationId: string): Promise<boolean> {
      const list = await accounts.list(organizationId)
      return list.length > 0
    },
  }
}

export type OnboardingRepository = ReturnType<typeof createOnboardingRepository>
