import { resolveSessionEntry } from '~/services/session-entry-resolver'
import { createOnboardingRepository } from '~/repositories/onboarding.repository'

export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore()

  if (!auth.initialized || auth.status === 'refreshing') {
    await auth.initializeSession()
  }

  if (!auth.isAuthenticated) {
    return navigateTo('/login')
  }

  const organization = useOrganizationStore()
  if (!organization.hydrated) {
    await organization.loadMemberships()
  }

  if (organization.memberships.length === 0) {
    if (!to.path.startsWith('/onboarding/organization')) {
      return navigateTo('/onboarding/organization')
    }
    return
  }

  if (!organization.currentOrganizationId && organization.memberships.length === 1) {
    organization.selectOrganization(organization.memberships[0]!.id)
  }

  if (!organization.currentOrganizationId) {
    if (to.path !== '/select-organization') {
      return navigateTo('/select-organization')
    }
    return
  }

  const orgId = organization.currentOrganizationId
  const onboarding = useOnboardingStore()
  const stored = onboarding.loadProgress(orgId)

  let hasAccount = false
  if (stored.markedComplete) {
    hasAccount = true
  } else if (!stored.skippedAccount) {
    try {
      const { $api } = useNuxtApp()
      const repo = createOnboardingRepository($api)
      hasAccount = await repo.hasAccount(orgId)
    } catch {
      hasAccount = false
    }
  }

  const destination = resolveSessionEntry({
    isAuthenticated: true,
    memberships: organization.memberships.map(m => ({ id: m.id })),
    currentOrganizationId: orgId,
    onboarding: {
      hasPreferences: stored.hasPreferences,
      hasAccount,
      skippedAccount: stored.skippedAccount,
      markedComplete: stored.markedComplete,
    },
  })

  const isAppRoute = to.path.startsWith('/app')
  const isOnboardingRoute = to.path.startsWith('/onboarding')

  if (isAppRoute && destination !== '/app/dashboard') {
    return navigateTo(destination)
  }

  if (isOnboardingRoute && destination === '/app/dashboard') {
    return navigateTo('/app/dashboard')
  }
})
