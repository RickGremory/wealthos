<script setup lang="ts">
import type { PlanningHorizon } from '~/types/planning'
import { planningHorizonLabel } from '~/composables/use-planning'

const model = defineModel<PlanningHorizon>({ required: true })

const options: PlanningHorizon[] = ['today', '7_days', '30_days', '90_days']
</script>

<template>
  <label class="horizon-selector">
    <span class="text-muted">Horizonte</span>
    <select v-model="model" aria-label="Horizonte de proyección">
      <option
        v-for="option in options"
        :key="option"
        :value="option"
      >
        {{ planningHorizonLabel(option) }}
      </option>
    </select>
  </label>
</template>

<style scoped>
.horizon-selector {
  display: inline-flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.85rem;
}
.horizon-selector select {
  min-width: 8rem;
  padding: 0.4rem 0.6rem;
  border-radius: 0.4rem;
  border: 1px solid var(--color-border, #d8dde6);
  background: var(--color-surface, #fff);
}
</style>
