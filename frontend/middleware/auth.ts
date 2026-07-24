export default defineNuxtRouteMiddleware(async () => {
  const auth = useAuthStore()

  if (!auth.initialized || auth.status === 'refreshing') {
    await auth.initializeSession()
  }

  if (!auth.isAuthenticated) {
    return navigateTo('/login')
  }
})
