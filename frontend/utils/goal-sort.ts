import type { GoalListItemView } from '~/types/goals'
import { compareDecimalStrings } from '~/utils/decimal-string'
import { toGoalPriority } from '~/utils/goal-priority'

/**
 * Sort: priority asc → target_date asc (nulls last) → completion desc.
 */
export function sortGoals(goals: GoalListItemView[]): GoalListItemView[] {
  return [...goals].sort((a, b) => {
    if (a.priority !== b.priority) return a.priority - b.priority

    const aDate = a.targetDate
    const bDate = b.targetDate
    if (aDate && bDate && aDate !== bDate) {
      return aDate < bDate ? -1 : 1
    }
    if (aDate && !bDate) return -1
    if (!aDate && bDate) return 1

    return compareDecimalStrings(b.completionPercentage, a.completionPercentage)
  })
}

/**
 * Primary goal for dashboard selection helper:
 * preferredPrimaryGoalId if active → else priority 1 → else nearest target_date → else highest completion.
 */
export function selectPrimaryGoalId(
  goals: GoalListItemView[],
  preferredPrimaryGoalId: string | null,
): string | null {
  const active = goals.filter(g => g.status === 'active')
  if (!active.length) return null

  if (preferredPrimaryGoalId) {
    const preferred = active.find(g => g.id === preferredPrimaryGoalId)
    if (preferred) return preferred.id
  }

  const highPriority = active.filter(g => toGoalPriority(g.priority) === 1)
  if (highPriority.length) {
    return sortGoals(highPriority)[0]!.id
  }

  const withDate = active
    .filter(g => g.targetDate)
    .sort((a, b) => (a.targetDate! < b.targetDate! ? -1 : 1))
  if (withDate.length) return withDate[0]!.id

  const byCompletion = [...active].sort((a, b) =>
    compareDecimalStrings(b.completionPercentage, a.completionPercentage),
  )
  return byCompletion[0]?.id ?? null
}
