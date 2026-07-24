import { defineStore } from 'pinia'
import { toUserMessage } from '~/lib/api/errors'
import { createAuthRepository } from '~/repositories/auth.repository'
import type { LoginInput, RegisterInput } from '~/repositories/auth.repository'
import type { UserSummary } from '~/types/domain'

/**
 * Auth token is stored in a cookie (`wealthos_access_token`) so SSR can read it.
 * This is NOT httpOnly — a future sprint should move to secure httpOnly cookies
 * set by a BFF / Nuxt server route.
 */
export const useAuthStore = defineStore('auth', () => {
  const tokenCookie = useCookie<string | null>('wealthos_access_token', {
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7,
    watch: true,
  })

  const token = computed(() => tokenCookie.value)
  const user = ref<UserSummary | null>(null)
  const loading = ref(false)
  const hydrated = ref(false)

  const isAuthenticated = computed(() => Boolean(tokenCookie.value))

  function setToken(value: string | null) {
    tokenCookie.value = value
  }

  async function login(input: LoginInput) {
    loading.value = true
    try {
      const { $api } = useNuxtApp()
      const repo = createAuthRepository($api)
      const payload = await repo.login(input)
      setToken(payload.accessToken)
      user.value = await repo.me()
      return user.value
    } catch (error) {
      throw new Error(toUserMessage(error), { cause: error })
    } finally {
      loading.value = false
    }
  }

  async function register(input: RegisterInput) {
    loading.value = true
    try {
      const { $api } = useNuxtApp()
      const repo = createAuthRepository($api)
      const payload = await repo.register(input)
      setToken(payload.accessToken)
      user.value = await repo.me()
      return user.value
    } catch (error) {
      throw new Error(toUserMessage(error), { cause: error })
    } finally {
      loading.value = false
    }
  }

  async function hydrate() {
    if (!tokenCookie.value) {
      user.value = null
      hydrated.value = true
      return
    }
    try {
      const { $api } = useNuxtApp()
      const repo = createAuthRepository($api)
      user.value = await repo.me()
    } catch {
      setToken(null)
      user.value = null
    } finally {
      hydrated.value = true
    }
  }

  function logout() {
    setToken(null)
    user.value = null
    const orgStore = useOrganizationStore()
    orgStore.clear()
    return navigateTo('/login')
  }

  return {
    token,
    user,
    loading,
    hydrated,
    isAuthenticated,
    setToken,
    login,
    register,
    hydrate,
    logout,
  }
})
