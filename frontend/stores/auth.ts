import { defineStore } from 'pinia'
import { toUserMessage } from '~/lib/api/errors'
import { createAuthRepository } from '~/repositories/auth.repository'
import type { LoginInput, RegisterInput } from '~/repositories/auth.repository'
import type { UserSummary } from '~/types/domain'

export type SessionStatus =
  | 'unknown'
  | 'authenticated'
  | 'unauthenticated'
  | 'refreshing'

/**
 * Auth token is stored in a cookie (`wealthos_access_token`) so SSR can read it.
 * This is NOT httpOnly — a future sprint should move to secure httpOnly cookies
 * set by a BFF / Nuxt server route.
 *
 * Callers navigate after login/register via `resolveSessionEntry` — this store
 * never navigates on success.
 */
export const useAuthStore = defineStore('auth', () => {
  const tokenCookie = useCookie<string | null>('wealthos_access_token', {
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7,
    watch: true,
  })

  const status = ref<SessionStatus>('unknown')
  const user = ref<UserSummary | null>(null)
  const initialized = ref(false)
  const loading = ref(false)

  const token = computed(() => tokenCookie.value)
  const isAuthenticated = computed(() => status.value === 'authenticated')

  function setToken(value: string | null) {
    tokenCookie.value = value
  }

  async function initializeSession() {
    if (initialized.value && status.value !== 'refreshing') {
      return
    }

    if (!tokenCookie.value) {
      user.value = null
      status.value = 'unauthenticated'
      initialized.value = true
      return
    }

    status.value = 'refreshing'
    try {
      const { $api } = useNuxtApp()
      const repo = createAuthRepository($api)
      user.value = await repo.me()
      status.value = 'authenticated'
    } catch {
      setToken(null)
      user.value = null
      status.value = 'unauthenticated'
    } finally {
      initialized.value = true
    }
  }

  async function login(input: LoginInput) {
    loading.value = true
    try {
      const { $api } = useNuxtApp()
      const repo = createAuthRepository($api)
      const payload = await repo.login(input)
      setToken(payload.accessToken)
      user.value = await repo.me()
      status.value = 'authenticated'
      initialized.value = true
      return user.value
    } catch (error) {
      status.value = 'unauthenticated'
      throw new Error(toUserMessage(error), { cause: error })
    } finally {
      loading.value = false
    }
  }

  async function register(input: Omit<RegisterInput, 'organizationName'> & {
    organizationName?: string
  }) {
    loading.value = true
    try {
      const { $api } = useNuxtApp()
      const repo = createAuthRepository($api)
      const organizationName =
        input.organizationName?.trim()
        || `${input.displayName.trim()} · Personal`

      const payload = await repo.register({
        ...input,
        organizationName,
      })
      setToken(payload.accessToken)
      user.value = await repo.me()
      status.value = 'authenticated'
      initialized.value = true
      return user.value
    } catch (error) {
      status.value = 'unauthenticated'
      throw new Error(toUserMessage(error), { cause: error })
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    setToken(null)
    user.value = null
    status.value = 'unauthenticated'
    initialized.value = true
    const orgStore = useOrganizationStore()
    orgStore.clear()
    return navigateTo('/login')
  }

  return {
    token,
    status,
    user,
    initialized,
    loading,
    isAuthenticated,
    setToken,
    initializeSession,
    login,
    register,
    logout,
  }
})
