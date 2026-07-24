import { createGoalsRepository } from '~/repositories/goals.repository'
import type { GoalListItemView, GoalSummaryView } from '~/types/goals'
import { toUserMessage } from '~/lib/api/errors'
import { addDecimalStrings, compareDecimalStrings } from '~/utils/decimal-string'
import { sortGoals } from '~/utils/goal-sort'
import { deriveGoalDisplayStatus } from '~/utils/goal-status'

export function applyGoalPriorities(
  goals: GoalListItemView[],
  getPriority: (goalId: string) => 1 | 2 | 3,
): GoalListItemView[] {
  return goals.map((goal) => {
    const priority = getPriority(goal.id)
    const display = deriveGoalDisplayStatus({
      status: goal.status,
      targetDate: goal.targetDate,
      estimatedCompletionDate: goal.estimatedCompletionDate,
      completionPercentage: goal.completionPercentage,
    })
    return {
      ...goal,
      priority,
      displayStatus: display.status,
    }
  })
}

export function computeGoalSummary(goals: GoalListItemView[]): GoalSummaryView {
  const active = goals.filter(g => g.status === 'active')
  if (!active.length) {
    return {
      activeCount: 0,
      accumulatedSavings: '0.00',
      averageProgress: '0',
      nearestGoalName: null,
      currency: null,
    }
  }

  // Prefer org-majority currency for the strip; fall back to first.
  const currencyCounts = new Map<string, number>()
  for (const g of active) {
    currencyCounts.set(g.currency, (currencyCounts.get(g.currency) ?? 0) + 1)
  }
  const currency = [...currencyCounts.entries()].sort((a, b) => b[1] - a[1])[0]![0]

  const sameCurrency = active.filter(g => g.currency === currency)
  const accumulatedSavings = addDecimalStrings(
    ...sameCurrency.map(g => g.currentAmount),
    '0.00',
  )

  const avg = sameCurrency.reduce(
    (sum, g) => sum + Number.parseFloat(g.completionPercentage || '0'),
    0,
  ) / sameCurrency.length

  const withDate = active
    .filter(g => g.targetDate)
    .sort((a, b) => (a.targetDate! < b.targetDate! ? -1 : 1))
  const nearestGoalName = withDate[0]?.name
    ?? [...active].sort((a, b) =>
      compareDecimalStrings(b.completionPercentage, a.completionPercentage),
    )[0]?.name
    ?? null

  return {
    activeCount: active.length,
    accumulatedSavings,
    averageProgress: avg.toFixed(1),
    nearestGoalName,
    currency,
  }
}

export function useGoals() {
  const organization = useOrganizationStore()
  const preferences = usePreferencesStore()
  const { $api } = useNuxtApp()
  const cache = useFinanceCache()

  const goals = ref<GoalListItemView[]>([])
  const listLoading = ref(false)
  const listError = ref<string | null>(null)
  const includeArchived = ref(false)

  const prioritizedGoals = computed(() =>
    applyGoalPriorities(goals.value, id => preferences.getGoalPriority(id)),
  )

  const sortedGoals = computed(() => sortGoals(prioritizedGoals.value))

  const visibleGoals = computed(() => {
    if (includeArchived.value) return sortedGoals.value
    return sortedGoals.value.filter(g => g.status !== 'archived')
  })

  const summary = computed(() => computeGoalSummary(prioritizedGoals.value))

  const hasAnyGoals = computed(() => goals.value.length > 0)
  const hasActiveGoals = computed(() => goals.value.some(g => g.status === 'active'))

  async function load() {
    const orgId = organization.currentOrganizationId
    if (!orgId) {
      listError.value = 'Selecciona una organización.'
      goals.value = []
      return
    }

    listLoading.value = true
    listError.value = null

    try {
      const repo = createGoalsRepository($api)
      goals.value = await repo.list(orgId, { includeArchived: true })
    }
    catch (e) {
      listError.value = toUserMessage(e)
      goals.value = []
    }
    finally {
      listLoading.value = false
    }
  }

  watch(
    () => cache.goalsVersion.value,
    () => {
      void load()
    },
  )

  return {
    goals,
    prioritizedGoals,
    sortedGoals,
    visibleGoals,
    summary,
    listLoading,
    listError,
    includeArchived,
    hasAnyGoals,
    hasActiveGoals,
    load,
  }
}
