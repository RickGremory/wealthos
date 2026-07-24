<script setup lang="ts">
import type { TransactionListItemView } from '~/types/transactions'
import { presentTransaction, displayAmountMagnitude } from '~/utils/transaction-presentation'
import { formatRelativeDay } from '~/composables/use-date'

const props = defineProps<{
  item: TransactionListItemView
}>()

const presentation = computed(() =>
  presentTransaction({
    type: props.item.type,
    status: props.item.status,
    signedAmount: props.item.signedAmount,
  }),
)

const subtitle = computed(() => {
  if (props.item.type === 'transfer') {
    return `${props.item.sourceAccountName || 'Origen'} → ${props.item.destinationAccountName || 'Destino'}`
  }
  return props.item.categoryName || props.item.accountName || ''
})

const displayAmount = computed(() => {
  const mag = displayAmountMagnitude(props.item.signedAmount || props.item.amount)
  if (presentation.value.amountPrefix === '-') return `-${mag}`
  if (presentation.value.amountPrefix === '+') return mag
  return mag
})
</script>

<template>
  <NuxtLink
    :to="`/app/transactions/${item.id}`"
    class="tx-item"
    data-testid="transaction-list-item"
  >
    <div class="tx-item__main">
      <p class="tx-item__title">{{ item.description }}</p>
      <p class="tx-item__meta text-muted">
        <TransactionTypeBadge :type="item.type" />
        <span v-if="subtitle">{{ subtitle }}</span>
        <span>{{ formatRelativeDay(item.occurredAt) }}</span>
      </p>
    </div>
    <div class="tx-item__right">
      <p
        class="tx-item__amount"
        :class="{
          'tx-item__amount--pos': presentation.presentationSign === 'positive',
          'tx-item__amount--neg': presentation.presentationSign === 'negative',
          'tx-item__amount--void': item.status === 'voided',
        }"
      >
        <span v-if="presentation.amountPrefix === '+'">+</span>
        <MoneyValue :amount="displayAmount" :currency="item.currency" />
      </p>
      <TransactionStatusBadge v-if="item.status === 'voided'" :status="item.status" />
    </div>
  </NuxtLink>
</template>

<style scoped>
.tx-item {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--color-border);
  text-decoration: none;
  color: inherit;
}

.tx-item:last-child {
  border-bottom: 0;
}

.tx-item__title {
  margin: 0;
  font-weight: 600;
}

.tx-item__meta {
  margin: 0.25rem 0 0;
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: center;
  font-size: 0.8rem;
}

.tx-item__right {
  text-align: right;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--space-1);
}

.tx-item__amount {
  margin: 0;
  font-variant-numeric: tabular-nums;
  font-weight: 700;
}

.tx-item__amount--pos {
  color: var(--color-positive);
}

.tx-item__amount--neg {
  color: var(--color-negative);
}

.tx-item__amount--void {
  opacity: 0.55;
  text-decoration: line-through;
}
</style>
