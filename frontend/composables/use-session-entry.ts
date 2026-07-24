import { resolveSessionEntry } from '~/services/session-entry-resolver'
import type { EntryDestination } from '~/services/session-entry-resolver'
import { createOnboardingRepository } from '~/repositories/onboarding.repository'
import { createLegalRepository } from '~/repositories/legal.repository'

/**
 * Boots auth + org memberships + onboarding progress for the current org,
 * then resolves where the user should land.
 *
 * Callers navigate — this composable never navigates by itself.
 */
export function useSessionEntry() {
  const auth = useAuthStore()
  const organization = useOrganizationStore()
  const onboarding = useOnboardingStore()

  async function initialize() {
    await auth.initializeSession()

    if (!auth.isAuthenticated) {
      return
    }

    if (!organization.hydrated) {
      await organization.loadMemberships()
    }

    const orgId = organization.currentOrganizationId
    if (orgId) {
      onboarding.loadProgress(orgId)
    }
  }

  async function buildOnboardingSnapshot(orgId: string | null) {
    if (!orgId) return null

    const stored = onboarding.getProgress(orgId)

    if (stored.markedComplete) {
      return {
        hasPreferences: stored.hasPreferences,
        hasAccount: true,
        skippedAccount: stored.skippedAccount,
        markedComplete: true,
      }
    }

    try {
      const { $api } = useNuxtApp()
      const repo = createOnboardingRepository($api)
      const composed = await repo.getProgress(orgId, stored)
      return {
        hasPreferences: composed.hasPreferences,
        hasAccount: composed.hasAccount,
        skippedAccount: composed.skippedAccount,
        markedComplete: composed.markedComplete,
      }
    } catch {
      return {
        hasPreferences: stored.hasPreferences,
        hasAccount: false,
        skippedAccount: stored.skippedAccount,
        markedComplete: stored.markedComplete,
      }
    }
  }

  async function fetchLegalCompliant(): Promise<boolean | null> {
    if (!auth.isAuthenticated) return null
    try {
      const { $api } = useNuxtApp()
      const repo = createLegalRepository($api)
      const status = await repo.getStatus()
      return status.isCompliant
    } catch {
      // Fail open for transient errors so users are not locked out of the app.
      return null
    }
  }

  async function resolveDestination(): Promise<EntryDestination> {
    await initialize()

    const legalCompliant = await fetchLegalCompliant()

    const orgId =
      organization.currentOrganizationId
      ?? (organization.memberships.length === 1
        ? organization.memberships[0]!.id
        : null)

    if (orgId && !organization.currentOrganizationId) {
      organization.selectOrganization(orgId)
    }

    if (orgId) {
      onboarding.loadProgress(orgId)
    }

    const snapshot = await buildOnboardingSnapshot(orgId)

    return resolveSessionEntry({
      isAuthenticated: auth.isAuthenticated,
      legalCompliant,
      memberships: organization.memberships.map(m => ({ id: m.id })),
      currentOrganizationId: organization.currentOrganizationId,
      onboarding: snapshot,
    })
  }

  return {
    initialize,
    resolveDestination,
    fetchLegalCompliant,
  }
}
