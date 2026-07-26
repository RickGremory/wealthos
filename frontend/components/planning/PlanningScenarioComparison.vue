<script setup lang="ts">
import type { ScenarioSimulation } from '~/types/planning'
import { planningStatusLabel } from '~/composables/use-planning'

defineProps<{
  simulation: ScenarioSimulation
}>()

const { format } = useMoney()
</script>

<template>
  <section class="comparison" aria-live="polite">
    <h2>Comparación del escenario</h2>
    <div class="comparison__grid">
      <article>
        <h3>Antes</h3>
        <p>{{ format(simulation.impact.safeToSpendBefore, simulation.baseline.currency) }}</p>
        <p class="text-muted">
          {{ planningStatusLabel(simulation.impact.statusBefore) }}
        </p>
      </article>
      <article>
        <h3>Después</h3>
        <p>{{ format(simulation.impact.safeToSpendAfter, simulation.scenario.currency) }}</p>
        <p class="text-muted">
          {{ planningStatusLabel(simulation.impact.statusAfter) }}
        </p>
      </article>
      <article>
        <h3>Delta Disponible</h3>
        <p>{{ format(simulation.impact.safeToSpendDelta, simulation.baseline.currency) }}</p>
        <p v-if="simulation.impact.statusChanged" class="text-muted">
          El estado cambió
        </p>
      </article>
    </div>
  </section>
</template>

<style scoped>
.comparison h2 {
  margin: 0 0 0.75rem;
  font-size: 1.05rem;
}
.comparison__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr));
  gap: 0.75rem;
}
.comparison__grid article {
  padding: 0.85rem 1rem;
  border-radius: 0.55rem;
  background: color-mix(in srgb, var(--color-surface, #fff) 90%, #64748b 10%);
}
.comparison__grid h3 {
  margin: 0;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-text-muted, #667);
}
.comparison__grid p {
  margin: 0.3rem 0 0;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
</style>
