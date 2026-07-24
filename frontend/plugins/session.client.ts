export default defineNuxtPlugin(async () => {
  const auth = useAuthStore()
  if (!auth.initialized) {
    await auth.initializeSession()
  }

  const organization = useOrganizationStore()
  if (auth.isAuthenticated && !organization.hydrated) {
    await organization.loadMemberships()
  }
})
