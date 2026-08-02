<script setup lang="ts">
import type { PlanningProjection } from '~/types/planning'

const props = defineProps<{
  projection: PlanningProjection
}>()

const { format } = useMoney()
const { formatDate } = useDate()

const upcoming = computed(() =>
  props.projection.timeline
    .filter(point =>
      point.cashFlowId != null
      || point.category === 'planned_cash_flow',
    )
    .slice(0, 8),
)
</script>

<template>
  <section class="upcoming">
    <h2>Próximos movimientos</h2>
    <UiEmptyState
      v-if="!upcoming.length"
      title="Sin movimientos en este horizonte"
      description="Agrega un ingreso o gasto planeado, o conecta obligaciones y metas."
    />
    <ul v-else class="upcoming__list">
      <li
        v-for="point in upcoming"
        :key="point.occurrenceKey || point.cashFlowId || point.occurredAt"
        class="upcoming__item"
      >
        <div>
          <p class="upcoming__label">
            {{ point.label }}
          </p>
          <p class="text-muted">
            {{ formatDate(point.occurredAt) }}
            · {{ point.direction === 'inflow' ? 'Ingreso' : 'Gasto' }}
          </p>
        </div>
        <p
          class="upcoming__amount"
          :data-direction="point.direction || undefined"
        >
          {{ point.direction === 'inflow' ? '+' : '−' }}
          {{ format(point.amount.replace('-', ''), projection.currency) }}
        </p>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.upcoming h2 {
  margin: 0 0 0.75rem;
  font-size: 1.05rem;
}
.upcoming__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.65rem;
}
.upcoming__item {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: baseline;
  padding: 0.65rem 0;
  border-bottom: 1px solid color-mix(in srgb, var(--color-border, #dde) 80%, transparent);
}
.upcoming__label {
  margin: 0;
  font-weight: 550;
}
.upcoming__amount {
  margin: 0;
  font-variant-numeric: tabular-nums;
  font-weight: 600;
}
.upcoming__amount[data-direction='inflow'] {
  color: var(--color-success, #0f7a4c);
}
.upcoming__amount[data-direction='outflow'] {
  color: var(--color-danger, #b42318);
}
</style>
