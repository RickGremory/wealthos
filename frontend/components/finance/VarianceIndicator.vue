<script setup lang="ts">
const props = defineProps<{
  value: string | null
  currency?: string
}>()

const { isNegativeDecimal, formatMoney } = useMoney()
const preferences = usePreferencesStore()

const direction = computed(() => {
  if (props.value == null || props.value === '' || props.value === '0' || props.value === '0.00') {
    return 'flat' as const
  }
  return isNegativeDecimal(props.value) ? 'down' : 'up'
})

const label = computed(() => {
  if (props.value == null) return '—'
  if (props.currency) {
    return formatMoney(props.value, props.currency, preferences.locale)
  }
  return props.value
})
</script>

<template>
  <span class="variance" :class="`variance--${direction}`">
    <span aria-hidden="true">{{ direction === 'up' ? '▲' : direction === 'down' ? '▼' : '●' }}</span>
    {{ label }}
  </span>
</template>

<style scoped>
.variance {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.85rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.variance--up {
  color: var(--color-positive);
}

.variance--down {
  color: var(--color-negative);
}

.variance--flat {
  color: var(--color-text-muted);
}
</style>
