<script setup lang="ts">
import type { TransactionListItemView } from '~/types/transactions'
import { presentTransaction, displayAmountMagnitude } from '~/utils/transaction-presentation'
import { formatDate } from '~/composables/use-date'

defineProps<{
  items: TransactionListItemView[]
  loading?: boolean
}>()

function rowAmount(item: TransactionListItemView) {
  const p = presentTransaction({
    type: item.type,
    status: item.status,
    signedAmount: item.signedAmount,
  })
  const mag = displayAmountMagnitude(item.signedAmount || item.amount)
  if (p.amountPrefix === '-') return `-${mag}`
  return mag
}

function rowSign(item: TransactionListItemView) {
  return presentTransaction({
    type: item.type,
    status: item.status,
    signedAmount: item.signedAmount,
  }).presentationSign
}
</script>

<template>
  <div class="tx-table-wrap" data-testid="transaction-table">
    <UiSkeleton v-if="loading" style="height: 12rem" />
    <table v-else class="tx-table">
      <thead>
        <tr>
          <th>Fecha</th>
          <th>Descripción</th>
          <th>Tipo</th>
          <th>Cuenta / Categoría</th>
          <th>Estado</th>
          <th class="tx-table__num">Monto</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ formatDate(item.occurredAt) }}</td>
          <td>
            <NuxtLink :to="`/app/transactions/${item.id}`">{{ item.description }}</NuxtLink>
          </td>
          <td><TransactionTypeBadge :type="item.type" /></td>
          <td class="text-muted">
            <template v-if="item.type === 'transfer'">
              {{ item.sourceAccountName }} → {{ item.destinationAccountName }}
            </template>
            <template v-else>
              {{ item.categoryName || item.accountName || '—' }}
            </template>
          </td>
          <td><TransactionStatusBadge :status="item.status" /></td>
          <td
            class="tx-table__num"
            :class="{
              'is-pos': rowSign(item) === 'positive',
              'is-neg': rowSign(item) === 'negative',
            }"
          >
            <span v-if="rowSign(item) === 'positive'">+</span>
            <MoneyValue :amount="rowAmount(item)" :currency="item.currency" />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.tx-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
}

.tx-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.tx-table th,
.tx-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.tx-table th {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-slate-600);
  background: var(--color-surface-muted);
}

.tx-table__num {
  text-align: right;
  font-variant-numeric: tabular-nums;
  font-weight: 600;
}

.is-pos {
  color: var(--color-positive);
}

.is-neg {
  color: var(--color-negative);
}

@media (max-width: 900px) {
  .tx-table-wrap {
    display: none;
  }
}
</style>
