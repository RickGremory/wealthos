export default defineNuxtPlugin(async () => {
  const auth = useAuthStore()
  if (auth.isAuthenticated && !auth.hydrated) {
    await auth.hydrate()
  }

  const organization = useOrganizationStore()
  if (auth.isAuthenticated && !organization.hydrated) {
    await organization.hydrate()
  }
})
