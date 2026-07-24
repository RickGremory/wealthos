export default defineNuxtRouteMiddleware(async () => {
  const auth = useAuthStore()

  if (!auth.initialized || auth.status === 'refreshing') {
    await auth.initializeSession()
  }

  if (!auth.isAuthenticated) {
    return
  }

  const { resolveDestination } = useSessionEntry()
  const destination = await resolveDestination()
  return navigateTo(destination)
})
