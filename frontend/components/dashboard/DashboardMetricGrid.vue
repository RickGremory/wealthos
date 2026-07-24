<script setup lang="ts">
import type { DashboardMetric } from '~/types/dashboard'

defineProps<{
  metrics: DashboardMetric[]
  loading?: boolean
}>()

const { format } = useMoney()
</script>

<template>
  <section class="metric-grid" aria-label="Métricas esenciales">
    <template v-if="loading">
      <MetricCard
        v-for="index in 4"
        :key="`skeleton-${index}`"
        label="Cargando"
        status="loading"
      />
    </template>
    <template v-else>
      <MetricCard
        v-for="metric in metrics"
        :key="metric.id"
        :label="metric.label"
        :amount="metric.amount"
        :currency="metric.currency"
        :hint="metric.hint"
        :trend-amount="metric.trendAmount"
        :trend-label="metric.trendLabel"
        :status="metric.status"
        :cta-label="metric.ctaLabel"
        :cta-to="metric.ctaTo"
      >
        <template v-if="metric.detailLines?.length" #details>
          <div
            v-for="line in metric.detailLines"
            :key="line.label"
            class="flow-line"
          >
            <span>{{ line.label }}</span>
            <strong>{{ format(line.amount, metric.currency) }}</strong>
          </div>
        </template>
      </MetricCard>
    </template>
  </section>
</template>

<style scoped>
.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--space-4);
}

.flow-line {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.flow-line strong {
  font-variant-numeric: tabular-nums;
  color: var(--color-text);
}

@media (max-width: 1100px) {
  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .metric-grid {
    grid-template-columns: 1fr;
  }
}
</style>
