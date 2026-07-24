import { defineStore } from 'pinia'
import type { GoalPriority } from '~/types/goals'
import { toGoalPriority } from '~/utils/goal-priority'

type GoalPrioritiesMap = Record<string, GoalPriority>

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

  const goalPrioritiesCookie = useCookie<GoalPrioritiesMap>('wealthos_goal_priorities', {
    default: () => ({}),
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 365,
  })

  const preferredPrimaryGoalIdCookie = useCookie<string | null>(
    'wealthos_preferred_primary_goal_id',
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

  const goalPriorities = computed({
    get: (): GoalPrioritiesMap => goalPrioritiesCookie.value ?? {},
    set: (value: GoalPrioritiesMap) => {
      goalPrioritiesCookie.value = value
    },
  })

  const preferredPrimaryGoalId = computed({
    get: () => preferredPrimaryGoalIdCookie.value || null,
    set: (value: string | null) => {
      preferredPrimaryGoalIdCookie.value = value
    },
  })

  function getGoalPriority(goalId: string): GoalPriority {
    return toGoalPriority(goalPriorities.value[goalId] ?? 2)
  }

  function setGoalPriority(goalId: string, priority: GoalPriority) {
    goalPriorities.value = {
      ...goalPriorities.value,
      [goalId]: toGoalPriority(priority),
    }
  }

  function toggleHideBalances() {
    hideBalances.value = !hideBalances.value
  }

  return {
    locale,
    hideBalances,
    preferredDashboardCurrency,
    goalPriorities,
    preferredPrimaryGoalId,
    getGoalPriority,
    setGoalPriority,
    toggleHideBalances,
  }
})
