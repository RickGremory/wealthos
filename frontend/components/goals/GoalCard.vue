<script setup lang="ts">
import type { GoalListItemView } from '~/types/goals'
import { getGoalPriorityLabel } from '~/utils/goal-priority'
import { getGoalStrategyLabel } from '~/utils/goal-strategies'
import { formatDate } from '~/composables/use-date'

const props = defineProps<{
  goal: GoalListItemView
  canWrite?: boolean
  canArchive?: boolean
}>()

const emit = defineEmits<{
  view: []
  edit: []
  archive: []
}>()

const priorityLabel = computed(() => getGoalPriorityLabel(props.goal.priority))
const strategyLabel = computed(() => getGoalStrategyLabel(props.goal.strategy))
const targetDateLabel = computed(() =>
  props.goal.targetDate ? formatDate(props.goal.targetDate) : 'Sin fecha',
)
</script>

<template>
  <article
    class="goal-card"
    :class="{ 'goal-card--archived': goal.status === 'archived' }"
    data-testid="goal-card"
    @click="emit('view')"
  >
    <div class="goal-card__top">
      <div class="stack-sm">
        <div class="goal-card__title-row">
          <h3 class="goal-card__name">{{ goal.name }}</h3>
          <GoalStatusBadge
            :status="goal.status"
            :display-status="goal.displayStatus"
            :target-date="goal.targetDate"
            :estimated-completion-date="goal.estimatedCompletionDate"
            :completion-percentage="goal.completionPercentage"
          />
        </div>
        <p class="goal-card__meta text-muted">
          {{ strategyLabel }} · Prioridad {{ priorityLabel }} · {{ targetDateLabel }}
        </p>
      </div>
      <CurrencyBadge :currency="goal.currency" />
    </div>

    <GoalProgressBar
      compact
      :completion-percentage="goal.completionPercentage"
      :remaining-amount="goal.remainingAmount"
      :currency="goal.currency"
      :current-amount="goal.currentAmount"
      :target-amount="goal.targetAmount"
    />

    <footer class="goal-card__footer">
      <span class="text-muted goal-card__footer-meta">
        Meta
        <MoneyValue :amount="goal.targetAmount" :currency="goal.currency" :emphasize-sign="false" />
      </span>
      <div class="goal-card__actions" @click.stop>
        <UiButton
          v-if="canWrite && goal.status !== 'archived'"
          type="button"
          size="sm"
          variant="ghost"
          @click="emit('edit')"
        >
          Editar
        </UiButton>
        <UiButton
          v-if="canArchive && goal.status !== 'archived'"
          type="button"
          size="sm"
          variant="ghost"
          @click="emit('archive')"
        >
          Archivar
        </UiButton>
      </div>
    </footer>
  </article>
</template>

<style scoped>
.goal-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  cursor: pointer;
  display: grid;
  gap: var(--space-4);
  min-width: 0;
  transition: border-color 140ms ease, box-shadow 140ms ease;
}

.goal-card:hover {
  border-color: var(--color-teal-600);
  box-shadow: var(--shadow-sm);
}

.goal-card--archived {
  opacity: 0.75;
}

.goal-card__top {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  align-items: flex-start;
  min-width: 0;
}

.goal-card__top > .stack-sm {
  min-width: 0;
  flex: 1 1 auto;
}

.goal-card__title-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
  min-width: 0;
}

.goal-card__name {
  margin: 0;
  font-size: 1.05rem;
  overflow-wrap: anywhere;
}

.goal-card__meta {
  margin: 0;
  font-size: 0.82rem;
  overflow-wrap: anywhere;
}

.goal-card__footer {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-2);
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border);
  min-width: 0;
}

.goal-card__footer-meta {
  font-size: 0.8rem;
  min-width: 0;
  overflow-wrap: anywhere;
}

.goal-card__actions {
  display: flex;
  flex-shrink: 0;
  gap: var(--space-1);
}
</style>
