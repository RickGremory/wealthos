<script setup lang="ts">
import type { GoalDisplayStatus, GoalStatus } from '~/types/goals'
import { deriveGoalDisplayStatus } from '~/utils/goal-status'

const props = defineProps<{
  status: GoalStatus
  displayStatus?: GoalDisplayStatus
  targetDate?: string | null
  estimatedCompletionDate?: string | null
  completionPercentage?: string
}>()

const meta = computed(() => {
  if (props.displayStatus) {
    return deriveGoalDisplayStatus({
      status: props.status,
      targetDate: props.targetDate ?? null,
      estimatedCompletionDate: props.estimatedCompletionDate ?? null,
      completionPercentage: props.completionPercentage ?? '0',
    })
  }
  return deriveGoalDisplayStatus({
    status: props.status,
    targetDate: props.targetDate ?? null,
    estimatedCompletionDate: props.estimatedCompletionDate ?? null,
    completionPercentage: props.completionPercentage ?? '0',
  })
})
</script>

<template>
  <UiBadge
    :tone="meta.tone"
    data-testid="goal-status-badge"
    :title="meta.hint"
  >
    {{ meta.label }}
  </UiBadge>
</template>
