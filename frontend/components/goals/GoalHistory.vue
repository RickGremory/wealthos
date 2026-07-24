<script setup lang="ts">
import type { GoalDetailView } from '~/types/goals'
import { formatDate } from '~/composables/use-date'

defineProps<{
  goal: GoalDetailView
}>()
</script>

<template>
  <div class="goal-history" data-testid="goal-history">
    <p class="text-muted goal-history__note">
      Aún no hay historial mensual de avances. Por ahora ves una foto del estado actual
      y el momento en que creaste la meta. Los snapshots mensuales llegarán más adelante.
    </p>

    <ol class="goal-history__list">
      <li class="goal-history__item">
        <div class="goal-history__dot" />
        <div class="stack-sm">
          <strong>Estado actual</strong>
          <p class="text-muted">
            <MoneyValue
              :amount="goal.currentAmount"
              :currency="goal.currency"
              :emphasize-sign="false"
            />
            de
            <MoneyValue
              :amount="goal.targetAmount"
              :currency="goal.currency"
              :emphasize-sign="false"
            />
            · {{ goal.completionPercentage }}%
          </p>
        </div>
      </li>
      <li v-if="goal.completedAt" class="goal-history__item">
        <div class="goal-history__dot goal-history__dot--success" />
        <div class="stack-sm">
          <strong>Completada</strong>
          <p class="text-muted">{{ formatDate(goal.completedAt) }}</p>
        </div>
      </li>
      <li v-if="goal.archivedAt" class="goal-history__item">
        <div class="goal-history__dot" />
        <div class="stack-sm">
          <strong>Archivada</strong>
          <p class="text-muted">{{ formatDate(goal.archivedAt) }}</p>
        </div>
      </li>
      <li class="goal-history__item">
        <div class="goal-history__dot" />
        <div class="stack-sm">
          <strong>Meta creada</strong>
          <p class="text-muted">{{ formatDate(goal.createdAt) }}</p>
        </div>
      </li>
    </ol>
  </div>
</template>

<style scoped>
.goal-history {
  display: grid;
  gap: var(--space-4);
}

.goal-history__note {
  margin: 0;
  font-size: 0.88rem;
}

.goal-history__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--space-4);
}

.goal-history__item {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: var(--space-3);
  align-items: start;
}

.goal-history__item p {
  margin: 0;
  font-size: 0.88rem;
}

.goal-history__dot {
  width: 0.65rem;
  height: 0.65rem;
  margin-top: 0.35rem;
  border-radius: 999px;
  background: var(--color-slate-400);
}

.goal-history__dot--success {
  background: var(--color-teal-600);
}
</style>
