<script setup lang="ts">
import type { PlanningBreakdownItem } from '~/types/planning'

defineProps<{
  items: PlanningBreakdownItem[]
  currency: string
}>()

const { format } = useMoney()
</script>

<template>
  <section class="breakdown">
    <h2>Desglose</h2>
    <ul>
      <li
        v-for="item in items.filter(i => i.included).slice(0, 12)"
        :key="item.id"
      >
        <div>
          <p>{{ item.label }}</p>
          <p class="text-muted">
            {{ item.sourceName }} · {{ item.category }}
          </p>
        </div>
        <p>
          {{ item.direction === 'subtract' ? '−' : '+' }}
          {{ format(item.amount, currency) }}
        </p>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.breakdown h2 {
  margin: 0 0 0.6rem;
  font-size: 1.05rem;
}
.breakdown ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.55rem;
}
.breakdown li {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.45rem 0;
}
.breakdown p {
  margin: 0;
}
</style>
