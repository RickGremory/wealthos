<script setup lang="ts">
import type { PlanningProjection } from '~/types/planning'

defineProps<{
  projection: PlanningProjection
}>()

const { format } = useMoney()
</script>

<template>
  <section class="summary-cards" aria-label="Resumen de proyección">
    <article>
      <h3>Saldo actual</h3>
      <p>{{ format(projection.currentAvailableCash, projection.currency) }}</p>
    </article>
    <article>
      <h3>Ingresos esperados</h3>
      <p>{{ format(projection.expectedIncome, projection.currency) }}</p>
    </article>
    <article>
      <h3>Compromisos</h3>
      <p>{{ format(projection.committedOutflows, projection.currency) }}</p>
    </article>
    <article>
      <h3>Protegido</h3>
      <p>{{ format(projection.protectedFunds, projection.currency) }}</p>
    </article>
    <article>
      <h3>Saldo mínimo</h3>
      <p>{{ format(projection.minimumProjectedBalance, projection.currency) }}</p>
    </article>
    <article>
      <h3>Saldo proyectado</h3>
      <p>{{ format(projection.projectedEndingBalance, projection.currency) }}</p>
    </article>
  </section>
</template>

<style scoped>
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(9.5rem, 1fr));
  gap: 0.75rem;
}
.summary-cards article {
  padding: 0.85rem 1rem;
  border-radius: 0.6rem;
  background: color-mix(in srgb, var(--color-surface, #fff) 92%, #94a3b8 8%);
}
.summary-cards h3 {
  margin: 0;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-text-muted, #667);
}
.summary-cards p {
  margin: 0.35rem 0 0;
  font-size: 1.1rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
</style>
