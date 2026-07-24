export default defineNuxtRouteMiddleware(async () => {
  const auth = useAuthStore()
  if (!auth.isAuthenticated) {
    return navigateTo('/login')
  }

  const organization = useOrganizationStore()
  if (!organization.hydrated) {
    await organization.hydrate()
  }

  if (!organization.currentOrganizationId) {
    return navigateTo('/onboarding')
  }
})
