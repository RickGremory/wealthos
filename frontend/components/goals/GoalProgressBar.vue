<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    completionPercentage: string
    remainingAmount: string
    currency: string
    currentAmount?: string
    targetAmount?: string
    compact?: boolean
  }>(),
  {
    currentAmount: undefined,
    targetAmount: undefined,
    compact: false,
  },
)

const pct = computed(() => {
  const n = Number.parseFloat(props.completionPercentage)
  if (!Number.isFinite(n)) return 0
  return Math.max(0, Math.min(100, n))
})

const pctLabel = computed(() => {
  const n = Number.parseFloat(props.completionPercentage)
  if (!Number.isFinite(n)) return '0%'
  return `${n % 1 === 0 ? n.toFixed(0) : n.toFixed(1)}%`
})
</script>

<template>
  <div
    class="goal-progress"
    :class="{ 'goal-progress--compact': compact }"
    data-testid="goal-progress-bar"
  >
    <div class="goal-progress__meta">
      <strong class="goal-progress__pct">{{ pctLabel }}</strong>
      <span class="text-muted goal-progress__remaining">
        Restan
        <MoneyValue :amount="remainingAmount" :currency="currency" :emphasize-sign="false" />
      </span>
    </div>
    <div
      class="goal-progress__track"
      role="progressbar"
      :aria-valuenow="pct"
      aria-valuemin="0"
      aria-valuemax="100"
    >
      <div class="goal-progress__fill" :style="{ width: `${pct}%` }" />
    </div>
    <div
      v-if="!compact && currentAmount != null && targetAmount != null"
      class="goal-progress__amounts text-muted"
    >
      <MoneyValue :amount="currentAmount" :currency="currency" :emphasize-sign="false" />
      <span>/</span>
      <MoneyValue :amount="targetAmount" :currency="currency" :emphasize-sign="false" />
    </div>
  </div>
</template>

<style scoped>
.goal-progress {
  display: grid;
  gap: var(--space-2);
}

.goal-progress__meta {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: var(--space-3);
}

.goal-progress__pct {
  font-size: 1.15rem;
  color: var(--color-teal-900);
  font-variant-numeric: tabular-nums;
}

.goal-progress--compact .goal-progress__pct {
  font-size: 0.95rem;
}

.goal-progress__remaining {
  font-size: 0.82rem;
}

.goal-progress__track {
  height: 0.65rem;
  border-radius: 999px;
  background: var(--color-slate-200);
  overflow: hidden;
}

.goal-progress--compact .goal-progress__track {
  height: 0.45rem;
}

.goal-progress__fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--color-teal-600), var(--color-teal-700));
  transition: width 220ms ease;
}

.goal-progress__amounts {
  display: flex;
  gap: 0.35rem;
  font-size: 0.8rem;
}
</style>
