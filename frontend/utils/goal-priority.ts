import type { GoalPriority } from '~/types/goals'

export const GOAL_PRIORITY_OPTIONS: Array<{ value: GoalPriority, label: string }> = [
  { value: 1, label: 'Alta' },
  { value: 2, label: 'Media' },
  { value: 3, label: 'Baja' },
]

export function getGoalPriorityLabel(priority: GoalPriority): string {
  return GOAL_PRIORITY_OPTIONS.find(o => o.value === priority)?.label ?? 'Media'
}

export function toGoalPriority(value: unknown): GoalPriority {
  if (value === 1 || value === '1') return 1
  if (value === 3 || value === '3') return 3
  return 2
}
