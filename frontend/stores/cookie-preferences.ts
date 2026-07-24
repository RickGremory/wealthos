import { defineStore } from 'pinia'

/**
 * Client-side cookie preference foundation.
 * Essentials are always on. Analytics/marketing default to false.
 * No complex banner until analytics is actually enabled.
 */
export const useCookiePreferencesStore = defineStore('cookiePreferences', () => {
  const cookie = useCookie<{
    analytics: boolean
    marketing: boolean
  }>('wealthos_cookie_prefs', {
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 365,
    default: () => ({ analytics: false, marketing: false }),
  })

  const essentials = computed(() => true)
  const analytics = computed({
    get: () => cookie.value?.analytics ?? false,
    set: (value: boolean) => {
      cookie.value = {
        analytics: value,
        marketing: cookie.value?.marketing ?? false,
      }
    },
  })
  const marketing = computed({
    get: () => cookie.value?.marketing ?? false,
    set: (value: boolean) => {
      cookie.value = {
        analytics: cookie.value?.analytics ?? false,
        marketing: value,
      }
    },
  })

  return {
    essentials,
    analytics,
    marketing,
  }
})
