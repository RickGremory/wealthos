<script setup lang="ts">
import type { AccountSummary } from '~/types/domain'
import type { CategoryTreeNodeView } from '~/types/categories'
import type { TransactionFiltersState } from '~/types/transactions'

const filters = defineModel<TransactionFiltersState>({ required: true })

const props = defineProps<{
  accounts: AccountSummary[]
  categories: CategoryTreeNodeView[]
}>()

const emit = defineEmits<{
  reset: []
}>()

const typeOptions = [
  { label: 'Todos los tipos', value: 'all' },
  { label: 'Gastos', value: 'expense' },
  { label: 'Ingresos', value: 'income' },
  { label: 'Transferencias', value: 'transfer' },
  { label: 'Ajustes', value: 'adjustment' },
]

const statusOptions = [
  { label: 'Todos los estados', value: 'all' },
  { label: 'Registrados', value: 'posted' },
  { label: 'Anulados', value: 'voided' },
]

const periodOptions = [
  { label: 'Este mes', value: 'this_month' },
  { label: 'Mes anterior', value: 'last_month' },
  { label: 'Últimos 30 días', value: 'last_30_days' },
  { label: 'Este año', value: 'this_year' },
  { label: 'Personalizado', value: 'custom' },
  { label: 'Todo', value: 'all' },
]

const accountOptions = computed(() => [
  { label: 'Todas las cuentas', value: '' },
  ...props.accounts.filter(a => a.isActive).map(a => ({
    label: a.name,
    value: a.id,
  })),
])

function flattenCats(nodes: CategoryTreeNodeView[], parent: string | null = null): Array<{ label: string, value: string }> {
  const out: Array<{ label: string, value: string }> = []
  for (const n of nodes) {
    if (n.isArchived) continue
    const label = parent ? `${parent} / ${n.name}` : n.name
    out.push({ label, value: n.id })
    if (n.children?.length) out.push(...flattenCats(n.children, n.name))
  }
  return out
}

const categoryOptions = computed(() => [
  { label: 'Todas las categorías', value: '' },
  ...flattenCats(props.categories),
])

const accountIdProxy = computed({
  get: () => filters.value.accountId ?? '',
  set: (v: string) => { filters.value.accountId = v || null },
})

const categoryIdProxy = computed({
  get: () => filters.value.categoryId ?? '',
  set: (v: string) => { filters.value.categoryId = v || null },
})
</script>

<template>
  <div class="tx-filters" data-testid="transaction-filters">
    <div class="tx-filters__grid">
      <UiInput
        v-model="filters.search"
        label="Buscar"
        placeholder="Descripción o notas"
      />
      <UiSelect
        v-model="filters.type"
        label="Tipo"
        :options="typeOptions"
      />
      <UiSelect
        v-model="filters.status"
        label="Estado"
        :options="statusOptions"
      />
      <UiSelect
        v-model="filters.period"
        label="Periodo"
        :options="periodOptions"
      />
      <UiSelect
        v-model="accountIdProxy"
        label="Cuenta"
        :options="accountOptions"
      />
      <UiSelect
        v-model="categoryIdProxy"
        label="Categoría"
        :options="categoryOptions"
      />
    </div>

    <div v-if="filters.period === 'custom'" class="tx-filters__custom cluster-sm">
      <UiInput
        :model-value="filters.dateFrom || ''"
        type="date"
        label="Desde"
        @update:model-value="filters.dateFrom = $event || null"
      />
      <UiInput
        :model-value="filters.dateTo || ''"
        type="date"
        label="Hasta"
        @update:model-value="filters.dateTo = $event || null"
      />
    </div>

    <div class="tx-filters__actions">
      <UiButton type="button" variant="ghost" size="sm" @click="emit('reset')">
        Limpiar filtros
      </UiButton>
    </div>
  </div>
</template>

<style scoped>
.tx-filters {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.tx-filters__grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-3);
}

.tx-filters__custom {
  flex-wrap: wrap;
}

.tx-filters__actions {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 800px) {
  .tx-filters__grid {
    grid-template-columns: 1fr;
  }
}
</style>
