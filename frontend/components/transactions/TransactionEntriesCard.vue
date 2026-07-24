<script setup lang="ts">
import type { TransactionEntryView } from '~/types/transactions'

defineProps<{
  entries: TransactionEntryView[]
}>()
</script>

<template>
  <UiCard data-testid="transaction-entries-card">
    <h2 class="entries-title">Asientos</h2>
    <ul class="entries-list">
      <li v-for="entry in entries" :key="entry.id" class="entries-list__item">
        <span>{{ entry.accountName || entry.accountId }}</span>
        <MoneyValue :amount="entry.amount" :currency="entry.currency" />
      </li>
    </ul>
  </UiCard>
</template>

<style scoped>
.entries-title {
  margin: 0 0 var(--space-3);
  font-size: 1rem;
}

.entries-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.entries-list__item {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--color-border);
  font-size: 0.9rem;
}

.entries-list__item:last-child {
  border-bottom: 0;
}
</style>
