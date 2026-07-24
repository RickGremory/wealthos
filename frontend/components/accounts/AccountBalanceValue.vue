<script setup lang="ts">
import type { BalancePresentation } from '~/utils/account-type-mapper'

withDefaults(
  defineProps<{
    amount: string
    currency: string
    prefix?: string | null
    presentation?: BalancePresentation
    label?: string
  }>(),
  {
    prefix: null,
    presentation: 'asset',
    label: undefined,
  },
)
</script>

<template>
  <div
    class="account-balance"
    :class="{
      'account-balance--liability': presentation === 'liability',
    }"
  >
    <span v-if="label" class="account-balance__label">{{ label }}</span>
    <p class="account-balance__value">
      <span v-if="prefix" class="account-balance__prefix">{{ prefix }}</span>
      <MoneyValue
        :amount="amount"
        :currency="currency"
        :emphasize-sign="presentation === 'asset'"
      />
    </p>
  </div>
</template>

<style scoped>
.account-balance__label {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-bottom: 0.15rem;
}

.account-balance__value {
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.35rem;
  font-size: 1.1rem;
}

.account-balance__prefix {
  font-weight: 600;
  color: var(--color-slate-700);
}

.account-balance--liability .account-balance__value {
  color: var(--color-ink);
}
</style>
