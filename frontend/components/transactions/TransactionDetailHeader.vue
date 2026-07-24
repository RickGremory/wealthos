<script setup lang="ts">
import type { TransactionDetailView } from '~/types/transactions'
import { formatDateTime } from '~/composables/use-date'
import { presentTransaction, displayAmountMagnitude } from '~/utils/transaction-presentation'

const props = defineProps<{
  transaction: TransactionDetailView
}>()

const presentation = computed(() =>
  presentTransaction({
    type: props.transaction.type,
    status: props.transaction.status,
    signedAmount: props.transaction.signedAmount,
  }),
)

const amount = computed(() =>
  displayAmountMagnitude(props.transaction.signedAmount || props.transaction.amount),
)
</script>

<template>
  <header class="tx-detail-header" data-testid="transaction-detail-header">
    <div class="tx-detail-header__top cluster-sm">
      <TransactionTypeBadge :type="transaction.type" />
      <TransactionStatusBadge :status="transaction.status" />
    </div>
    <h1 class="tx-detail-header__title">{{ transaction.description }}</h1>
    <p
      class="tx-detail-header__amount"
      :class="{
        'is-pos': presentation.presentationSign === 'positive',
        'is-neg': presentation.presentationSign === 'negative',
      }"
    >
      <span v-if="presentation.amountPrefix">{{ presentation.amountPrefix }}</span>
      <MoneyValue :amount="amount" :currency="transaction.currency" />
    </p>
    <p class="text-muted">{{ formatDateTime(transaction.occurredAt) }}</p>
  </header>
</template>

<style scoped>
.tx-detail-header__title {
  margin: var(--space-2) 0 0;
  font-size: 1.5rem;
}

.tx-detail-header__amount {
  margin: var(--space-3) 0 var(--space-1);
  font-size: 1.75rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.is-pos {
  color: var(--color-positive);
}

.is-neg {
  color: var(--color-negative);
}
</style>
