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
        <strong
          class="goal-summary__value goal-summary__value--name"
          :title="summary.nearestGoalName || undefined"
        >
          {{ summary.nearestGoalName || '—' }}
        </strong>
      </div>
    </div>
  </section>
</template>

<style scoped>
.goal-summary {
  min-width: 0;
}

.goal-summary__grid {
  display: grid;
  gap: var(--space-3);
  grid-template-columns: repeat(2, minmax(0, 1fr));
  min-width: 0;
}

@media (min-width: 900px) {
  .goal-summary__grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

.goal-summary__metric {
  min-width: 0;
  overflow: hidden;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-1);
}

.goal-summary__label {
  font-size: 0.75rem;
  line-height: 1.25;
  color: var(--color-text-muted);
  overflow-wrap: anywhere;
}

.goal-summary__value {
  display: block;
  min-width: 0;
  max-width: 100%;
  font-size: clamp(0.95rem, 3.6vw, 1.2rem);
  line-height: 1.2;
  color: var(--color-teal-900);
  font-variant-numeric: tabular-nums;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.goal-summary__value :deep(.money-value) {
  display: inline;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.goal-summary__value--name {
  font-size: clamp(0.9rem, 3.2vw, 1rem);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 380px) {
  .goal-summary__grid {
    grid-template-columns: 1fr;
  }
}
</style>
