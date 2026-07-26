<script setup lang="ts">
import type { PlanningProjection } from '~/types/planning'
import {
  planningConfidenceLabel,
  planningStatusLabel,
} from '~/composables/use-planning'

defineProps<{
  projection: PlanningProjection | null
  loading?: boolean
}>()

const { format } = useMoney()
</script>

<template>
  <section class="planning-hero" aria-live="polite">
    <p class="planning-hero__eyebrow">
      Disponible para usar
    </p>
    <div v-if="loading" class="planning-hero__amount">
      <UiSkeleton height="2.5rem" width="12rem" />
    </div>
    <p v-else class="planning-hero__amount">
      <template v-if="projection?.safeToSpend == null">
        —
      </template>
      <template v-else>
        {{ format(projection.safeToSpend, projection.currency) }}
      </template>
    </p>
    <p v-if="projection" class="planning-hero__meta text-muted">
      {{ planningStatusLabel(projection.status) }}
      · Confianza {{ planningConfidenceLabel(projection.confidence).toLowerCase() }}
    </p>
  </section>
</template>

<style scoped>
.planning-hero {
  padding: 1.5rem 0 0.5rem;
}
.planning-hero__eyebrow {
  margin: 0;
  font-size: 0.95rem;
  letter-spacing: 0.02em;
  color: var(--color-text-muted, #667);
}
.planning-hero__amount {
  margin: 0.35rem 0;
  font-size: clamp(2rem, 4vw, 2.75rem);
  font-weight: 650;
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}
.planning-hero__meta {
  margin: 0;
  font-size: 0.95rem;
}
</style>
