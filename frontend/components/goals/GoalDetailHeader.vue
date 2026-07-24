<script setup lang="ts">
import type { GoalDetailView } from '~/types/goals'
import { getGoalPriorityLabel } from '~/utils/goal-priority'
import { getGoalStrategyLabel } from '~/utils/goal-strategies'
import { formatDate } from '~/composables/use-date'

const props = defineProps<{
  goal: GoalDetailView
  canWrite?: boolean
  canArchive?: boolean
}>()

const emit = defineEmits<{
  edit: []
  archive: []
}>()

const priorityLabel = computed(() => getGoalPriorityLabel(props.goal.priority))
</script>

<template>
  <header class="detail-header" data-testid="goal-detail-header">
    <div class="stack-sm">
      <div class="detail-header__badges">
        <GoalStatusBadge
          :status="goal.status"
          :display-status="goal.displayStatus"
          :target-date="goal.targetDate"
          :estimated-completion-date="goal.estimatedCompletionDate"
          :completion-percentage="goal.completionPercentage"
        />
        <CurrencyBadge :currency="goal.currency" />
        <UiBadge tone="neutral">Prioridad {{ priorityLabel }}</UiBadge>
      </div>
      <h1 class="detail-header__title">{{ goal.name }}</h1>
      <p class="text-muted detail-header__subtitle">
        {{ getGoalStrategyLabel(goal.strategy) }}
        <template v-if="goal.targetDate">
          · Objetivo {{ formatDate(goal.targetDate) }}
        </template>
      </p>
    </div>

    <div class="detail-header__actions">
      <UiButton
        v-if="canWrite && goal.status !== 'archived'"
        type="button"
        variant="secondary"
        @click="emit('edit')"
      >
        Editar
      </UiButton>
      <UiButton
        v-if="canArchive && goal.status !== 'archived'"
        type="button"
        variant="ghost"
        @click="emit('archive')"
      >
        Archivar
      </UiButton>
    </div>
  </header>
</template>

<style scoped>
.detail-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}

.detail-header__badges {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.detail-header__title {
  margin: 0;
  font-size: clamp(1.5rem, 2.5vw, 1.9rem);
}

.detail-header__subtitle {
  margin: 0;
}

.detail-header__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: flex-start;
}
</style>
