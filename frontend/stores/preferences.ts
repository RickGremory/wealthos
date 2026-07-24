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

  const preferredDashboardCurrencyCookie = useCookie<string | null>(
    'wealthos_dashboard_currency',
    {
      default: () => null,
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 365,
    },
  )

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

  const preferredDashboardCurrency = computed({
    get: () => preferredDashboardCurrencyCookie.value || null,
    set: (value: string | null) => {
      preferredDashboardCurrencyCookie.value = value
    },
  })

  function toggleHideBalances() {
    hideBalances.value = !hideBalances.value
  }

  return {
    locale,
    hideBalances,
    preferredDashboardCurrency,
    toggleHideBalances,
  }
})
