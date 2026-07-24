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
    if (to.path !== '/onboarding/organization') {
      return navigateTo('/onboarding/organization')
    }
    return
  }

  if (!organization.currentOrganizationId && organization.memberships.length === 1) {
    organization.selectOrganization(organization.memberships[0]!.id)
  }

  if (!organization.currentOrganizationId && organization.memberships.length > 1) {
    if (to.path !== '/select-organization') {
      return navigateTo('/select-organization')
    }
  }
})
