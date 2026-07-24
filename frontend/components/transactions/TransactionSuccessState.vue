<script setup lang="ts">
import type { TransactionDetailView } from '~/types/transactions'

defineProps<{
  transaction: TransactionDetailView
}>()

const emit = defineEmits<{
  view: []
  another: []
  undo: []
}>()
</script>

<template>
  <div class="tx-success" data-testid="transaction-success">
    <p class="tx-success__eyebrow">Registrado</p>
    <h3 class="tx-success__title">{{ transaction.description }}</h3>
    <p class="tx-success__amount">
      <MoneyValue :amount="transaction.amount" :currency="transaction.currency" />
    </p>
    <div class="tx-success__actions cluster-sm">
      <UiButton type="button" size="sm" variant="primary" @click="emit('view')">
        Ver
      </UiButton>
      <UiButton type="button" size="sm" variant="secondary" @click="emit('another')">
        Registrar otro
      </UiButton>
      <UiButton type="button" size="sm" variant="ghost" @click="emit('undo')">
        Deshacer
      </UiButton>
    </div>
  </div>
</template>

<style scoped>
.tx-success {
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  background: linear-gradient(160deg, var(--color-teal-50), var(--color-surface));
  border: 1px solid var(--color-teal-100);
}

.tx-success__eyebrow {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-teal-800);
}

.tx-success__title {
  margin: var(--space-1) 0 0;
  font-size: 1.1rem;
}

.tx-success__amount {
  margin: var(--space-2) 0 var(--space-4);
  font-size: 1.25rem;
}

.tx-success__actions {
  flex-wrap: wrap;
}
</style>
