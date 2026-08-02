<script setup lang="ts">
import type { TransactionListItemView } from '~/types/transactions'
import { formatDate } from '~/composables/use-date'

const props = defineProps<{
  items: TransactionListItemView[]
  loading?: boolean
  loadingMore?: boolean
  hasMore?: boolean
  filtersActive?: boolean
}>()

const emit = defineEmits<{
  loadMore: []
  clearFilters: []
}>()

const grouped = computed(() => {
  const map = new Map<string, TransactionListItemView[]>()
  for (const item of props.items) {
    const key = item.occurredAt.slice(0, 10)
    const list = map.get(key) ?? []
    list.push(item)
    map.set(key, list)
  }
  return [...map.entries()].map(([date, rows]) => ({
    date,
    label: formatDate(date),
    items: rows,
  }))
})
</script>

<template>
  <div class="tx-list" data-testid="transaction-list">
    <div v-if="loading" class="stack">
      <UiSkeleton v-for="n in 4" :key="n" style="height: 3.5rem" />
    </div>

    <UiEmptyState
      v-else-if="!items.length"
      :title="filtersActive ? 'Ningún movimiento con estos filtros' : 'Sin movimientos'"
      :description="filtersActive
        ? 'Prueba limpiar filtros o ampliar el periodo.'
        : 'Ajusta los filtros o registra tu primera transacción.'"
    >
      <template v-if="filtersActive" #actions>
        <UiButton type="button" variant="secondary" @click="emit('clearFilters')">
          Limpiar filtros
        </UiButton>
      </template>
    </UiEmptyState>

    <div v-else class="stack">
      <section v-for="group in grouped" :key="group.date" class="tx-list__group">
        <h3 class="tx-list__day">{{ group.label }}</h3>
        <TransactionListItem
          v-for="item in group.items"
          :key="item.id"
          :item="item"
        />
      </section>

      <div v-if="hasMore" class="tx-list__more">
        <UiButton
          type="button"
          variant="secondary"
          :loading="loadingMore"
          @click="emit('loadMore')"
        >
          Cargar más
        </UiButton>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tx-list__group {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-4);
}

.tx-list__day {
  margin: 0 0 var(--space-2);
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--color-slate-600);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.tx-list__more {
  display: flex;
  justify-content: center;
  padding: var(--space-2) 0;
}
</style>
