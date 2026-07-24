<script setup lang="ts">
import type { DashboardRecentTransaction } from '~/types/dashboard'

defineProps<{
  items: DashboardRecentTransaction[]
  loading?: boolean
}>()

const { formatDate } = useDate()

function signedAmount(item: DashboardRecentTransaction): string {
  if (item.transactionType === 'expense') return `-${item.amount}`
  if (item.transactionType === 'income') return item.amount
  return item.amount
}

function isOpeningBalance(item: DashboardRecentTransaction): boolean {
  return (
    item.transactionType === 'adjustment'
    && item.description.toLowerCase().startsWith('saldo inicial')
  )
}

function typeLabel(item: DashboardRecentTransaction): string {
  if (isOpeningBalance(item)) return 'Saldo inicial'
  return item.categoryName || item.transactionType
}
</script>

<template>
  <UiCard title="Actividad reciente">
    <template #header>
      <div class="recent__actions">
        <NuxtLink to="/app/transactions">Ver movimientos</NuxtLink>
      </div>
    </template>

    <div v-if="loading" class="stack">
      <UiSkeleton v-for="i in 4" :key="i" height="2.5rem" />
    </div>

    <UiEmptyState
      v-else-if="!items.length"
      title="Sin movimientos aún"
      description="Registra un ingreso o gasto para empezar a ver actividad aquí."
    >
      <template #actions>
        <UiButton type="button" @click="navigateTo('/app/transactions')">
          Registrar movimiento
        </UiButton>
      </template>
    </UiEmptyState>

    <ul v-else class="recent__list">
      <li
        v-for="item in items"
        :key="item.id"
        class="recent__item"
        :data-neutral="isOpeningBalance(item)"
      >
        <div class="stack-sm">
          <p class="recent__desc">{{ item.description }}</p>
          <p class="recent__meta text-muted">
            <span>{{ typeLabel(item) }}</span>
            <span>·</span>
            <span>{{ item.accountName || 'Sin cuenta' }}</span>
            <span>·</span>
            <span>{{ formatDate(item.occurredAt) }}</span>
          </p>
        </div>
        <p class="recent__amount" :class="{ 'recent__amount--neutral': isOpeningBalance(item) }">
          <MoneyValue
            :amount="signedAmount(item)"
            :currency="item.currency"
          />
        </p>
      </li>
    </ul>
  </UiCard>
</template>

<style scoped>
.recent__actions {
  margin-left: auto;
  font-size: 0.85rem;
}

.recent__actions a {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 600;
}

.recent__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--space-3);
}

.recent__item {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
  align-items: center;
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--color-border);
}

.recent__item:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.recent__desc {
  margin: 0;
  font-weight: 600;
}

.recent__meta {
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  font-size: 0.8rem;
}

.recent__amount {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.05rem;
  white-space: nowrap;
}

.recent__amount--neutral :deep(.money-value),
.recent__amount--neutral {
  color: var(--color-text-muted);
  font-weight: 600;
}

.recent__item[data-neutral='true'] .recent__desc {
  font-weight: 500;
  color: var(--color-text-muted);
}
</style>
