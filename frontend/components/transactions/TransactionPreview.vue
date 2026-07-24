<script setup lang="ts">
import type { TransactionType } from '~/types/transactions'
import { computeAdjustmentDelta } from '~/utils/transaction-payload'
import { displayAmountMagnitude } from '~/utils/transaction-presentation'

const props = defineProps<{
  type: TransactionType
  amount?: string
  realBalance?: string
  currentBalance?: string
  currency?: string
  sourceName?: string | null
  destinationName?: string | null
  accountName?: string | null
}>()

const adjustmentDelta = computed(() => {
  if (props.type !== 'adjustment') return null
  return computeAdjustmentDelta(props.realBalance || '0', props.currentBalance || '0')
})

const deltaPositive = computed(() => {
  const d = adjustmentDelta.value
  if (!d) return true
  return !d.trim().startsWith('-')
})
</script>

<template>
  <div v-if="type === 'transfer' || type === 'adjustment'" class="tx-preview" data-testid="transaction-preview">
    <template v-if="type === 'transfer'">
      <p class="tx-preview__title">Vista previa</p>
      <p class="tx-preview__line">
        <span>{{ sourceName || 'Origen' }}</span>
        <span class="tx-preview__arrow">→</span>
        <span>{{ destinationName || 'Destino' }}</span>
      </p>
      <p v-if="amount" class="tx-preview__amount">
        <MoneyValue
          :amount="displayAmountMagnitude(amount)"
          :currency="currency || 'MXN'"
        />
      </p>
    </template>

    <template v-else>
      <p class="tx-preview__title">Ajuste calculado</p>
      <p class="tx-preview__meta text-muted">
        {{ accountName || 'Cuenta' }} · saldo actual
        <MoneyValue :amount="currentBalance || '0.00'" :currency="currency || 'MXN'" />
        → real
        <MoneyValue :amount="realBalance || '0.00'" :currency="currency || 'MXN'" />
      </p>
      <p
        class="tx-preview__amount"
        :class="deltaPositive ? 'tx-preview__amount--pos' : 'tx-preview__amount--neg'"
      >
        Delta:
        <MoneyValue :amount="adjustmentDelta" :currency="currency || 'MXN'" />
      </p>
    </template>
  </div>
</template>

<style scoped>
.tx-preview {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  background: var(--color-teal-50);
  border: 1px solid var(--color-teal-100);
}

.tx-preview__title {
  margin: 0 0 var(--space-2);
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--color-teal-900);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.tx-preview__line {
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-wrap: wrap;
  font-weight: 600;
}

.tx-preview__arrow {
  color: var(--color-teal-700);
}

.tx-preview__amount {
  margin: var(--space-2) 0 0;
  font-size: 1.05rem;
}

.tx-preview__amount--pos {
  color: var(--color-positive);
}

.tx-preview__amount--neg {
  color: var(--color-negative);
}

.tx-preview__meta {
  margin: 0;
  font-size: 0.85rem;
}
</style>
