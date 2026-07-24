<script setup lang="ts">
import type { GoalSummaryView } from '~/types/goals'

defineProps<{
  summary: GoalSummaryView
  loading?: boolean
}>()
</script>

<template>
  <section class="goal-summary" aria-label="Resumen de metas" data-testid="goal-summary">
    <div v-if="loading" class="goal-summary__grid">
      <UiSkeleton height="5.5rem" />
      <UiSkeleton height="5.5rem" />
      <UiSkeleton height="5.5rem" />
      <UiSkeleton height="5.5rem" />
    </div>
    <div v-else class="goal-summary__grid">
      <div class="goal-summary__metric">
        <span class="goal-summary__label">Activas</span>
        <strong class="goal-summary__value">{{ summary.activeCount }}</strong>
      </div>
      <div class="goal-summary__metric">
        <span class="goal-summary__label">Ahorro acumulado</span>
        <strong class="goal-summary__value">
          <template v-if="summary.currency">
            <MoneyValue
              :amount="summary.accumulatedSavings"
              :currency="summary.currency"
              :emphasize-sign="false"
            />
          </template>
          <template v-else>—</template>
        </strong>
      </div>
      <div class="goal-summary__metric">
        <span class="goal-summary__label">Avance promedio</span>
        <strong class="goal-summary__value">{{ summary.averageProgress }}%</strong>
      </div>
      <div class="goal-summary__metric">
        <span class="goal-summary__label">Más cercana</span>
        <strong class="goal-summary__value goal-summary__value--name">
          {{ summary.nearestGoalName || '—' }}
        </strong>
      </div>
    </div>
  </section>
</template>

<style scoped>
.goal-summary__grid {
  display: grid;
  gap: var(--space-3);
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

@media (min-width: 900px) {
  .goal-summary__grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

.goal-summary__metric {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  display: grid;
  gap: var(--space-2);
}

.goal-summary__label {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.goal-summary__value {
  font-size: 1.25rem;
  color: var(--color-teal-900);
  font-variant-numeric: tabular-nums;
}

.goal-summary__value--name {
  font-size: 1rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
