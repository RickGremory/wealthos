<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    amount: string | null
    currency: string
    emphasizeSign?: boolean
    locale?: string
  }>(),
  {
    emphasizeSign: true,
    locale: undefined,
  },
)

const { format, isNegativeDecimal } = useMoney()

const formatted = computed(() =>
  format(props.amount, props.currency, props.locale),
)

const negative = computed(() => isNegativeDecimal(props.amount))
</script>

<template>
  <span
    class="money-value"
    :class="{
      'money-value--negative': emphasizeSign && negative,
      'money-value--positive': emphasizeSign && !negative && amount != null && amount !== '',
    }"
  >
    {{ formatted }}
  </span>
</template>

<style scoped>
.money-value {
  font-variant-numeric: tabular-nums;
  font-weight: 600;
}

.money-value--negative {
  color: var(--color-negative);
}

.money-value--positive {
  color: var(--color-ink);
}
</style>
