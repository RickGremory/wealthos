<script setup lang="ts">
import type { DashboardCashFlowSummary } from '~/types/dashboard'

defineProps<{
  cashFlow: DashboardCashFlowSummary
}>()

const { format } = useMoney()
</script>

<template>
  <UiCard
    v-if="cashFlow.status === 'ready'"
    title="Flujo de caja del mes"
    data-testid="dashboard-cash-flow"
  >
    <div class="cash-flow stack">
      <div class="cash-flow__row">
        <span>Ingresos</span>
        <strong>{{ format(cashFlow.income || '0.00', cashFlow.currency || 'MXN') }}</strong>
      </div>
      <div class="cash-flow__row">
        <span>Gastos</span>
        <strong>{{ format(cashFlow.expenses || '0.00', cashFlow.currency || 'MXN') }}</strong>
      </div>
      <div class="cash-flow__row cash-flow__row--net">
        <span>Neto</span>
        <strong>{{ format(cashFlow.netCashFlow || '0.00', cashFlow.currency || 'MXN') }}</strong>
      </div>
      <p v-if="cashFlow.points.length" class="text-muted cash-flow__hint">
        {{ cashFlow.points.length }} días con serie diaria
      </p>
    </div>
  </UiCard>
</template>

<style scoped>
.cash-flow__row {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  font-size: 0.92rem;
}

.cash-flow__row--net {
  padding-top: var(--space-2);
  border-top: 1px solid var(--color-border);
  font-weight: 700;
}

.cash-flow__hint {
  margin: 0;
  font-size: 0.8rem;
}
</style>
