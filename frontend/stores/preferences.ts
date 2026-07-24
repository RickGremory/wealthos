import { defineStore } from 'pinia'

export const usePreferencesStore = defineStore('preferences', () => {
  const localeCookie = useCookie<string>('wealthos_locale', {
    default: () => 'es-MX',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 365,
  })

  const hideBalancesCookie = useCookie<boolean>('wealthos_hide_balances', {
    default: () => false,
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 365,
  })

  const locale = computed({
    get: () => localeCookie.value || 'es-MX',
    set: (value: string) => {
      localeCookie.value = value
    },
  })

  const hideBalances = computed({
    get: () => Boolean(hideBalancesCookie.value),
    set: (value: boolean) => {
      hideBalancesCookie.value = value
    },
  })

  function toggleHideBalances() {
    hideBalances.value = !hideBalances.value
  }

  return {
    locale,
    hideBalances,
    toggleHideBalances,
  }
})
