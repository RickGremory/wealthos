import { createLegalRepository } from '~/repositories/legal.repository'

/**
 * Redirect authenticated users who are not legally compliant to /legal/review.
 * Skips /legal/* to avoid loops.
 */
export default defineNuxtRouteMiddleware(async (to) => {
  if (to.path.startsWith('/legal')) {
    return
  }

  const isGuarded
    = to.path.startsWith('/app')
      || to.path.startsWith('/onboarding')
      || to.path === '/select-organization'

  if (!isGuarded) {
    return
  }

  const auth = useAuthStore()
  if (!auth.initialized || auth.status === 'refreshing') {
    await auth.initializeSession()
  }

  if (!auth.isAuthenticated) {
    return
  }

  try {
    const { $api } = useNuxtApp()
    const repo = createLegalRepository($api)
    const status = await repo.getStatus()
    if (!status.isCompliant) {
      return navigateTo('/legal/review')
    }
  } catch {
    // Fail open on transient API errors.
  }
})
