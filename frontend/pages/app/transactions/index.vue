<script setup lang="ts">
import { hasActiveFilters } from '~/utils/transaction-filters'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const composer = useTransactionComposerStore()
const { canWrite } = useOrganizationPermissions()
const cache = useFinanceCache()
const route = useRoute()

const {
  filters,
  resetFilters,
  applyFilters,
} = useTransactionFilters()

const {
  items,
  total,
  loading,
  loadingMore,
  error,
  accounts,
  categories,
  hasMore,
  summary,
  load,
  loadMore,
} = useTransactions()

const organization = useOrganizationStore()

const filtersActive = computed(() => hasActiveFilters(filters.value))
const showEmpty = computed(() => !loading.value && !error.value && total.value === 0)

const emptyTitle = computed(() => {
  if (filtersActive.value) return 'Ningún movimiento con estos filtros'
  if (filters.value.period === 'this_month') return 'Sin movimientos este mes'
  return 'Sin movimientos'
})

const emptyDescription = computed(() => {
  if (filtersActive.value) {
    return 'Puede haber datos fuera de tipo, estado o periodo. Usa «Limpiar filtros» o cambia el periodo a «Todo».'
  }
  if (filters.value.period === 'this_month') {
    return 'El periodo por defecto es el mes en curso. Amplía a «Todo» para ver el historial completo.'
  }
  return 'Registra tu primera transacción para empezar.'
})

async function refresh() {
  await load(filters.value, { reset: true })
}

function showAllPeriods() {
  applyFilters({ period: 'all' })
}

onMounted(async () => {
  await refresh()
  if (route.query.new === '1' || route.query.new === 'true') {
    composer.openCreate('expense')
    const { new: _drop, ...rest } = route.query
    void navigateTo({ query: rest }, { replace: true })
    return
  }

  const type = String(route.query.type ?? '')
  const destination = String(route.query.destination_account_id ?? '')
  if (type === 'transfer' || destination) {
    composer.openWithDraft(
      {
        type: 'transfer',
        destinationAccountId: destination || undefined,
        sourceAccountId: route.query.source_account_id
          ? String(route.query.source_account_id)
          : undefined,
        amount: route.query.amount ? String(route.query.amount) : undefined,
        description: route.query.description
          ? String(route.query.description)
          : undefined,
      },
      {
        label: String(route.query.source ?? '') === 'commitment'
          ? 'Pago de obligación'
          : undefined,
      },
    )
    void navigateTo({ path: '/app/transactions', query: {} }, { replace: true })
  }
})

watch(
  () => organization.currentOrganizationId,
  () => { void refresh() },
)

watch(
  () => cache.transactionsVersion.value,
  () => { void refresh() },
)

// Debounce search; refresh immediately for other filter changes.
let searchTimer: ReturnType<typeof setTimeout> | null = null
watch(
  () => filters.value.search,
  () => {
    if (searchTimer) clearTimeout(searchTimer)
    searchTimer = setTimeout(() => {
      void refresh()
    }, 300)
  },
)

watch(
  () => ({
    type: filters.value.type,
    status: filters.value.status,
    accountId: filters.value.accountId,
    categoryId: filters.value.categoryId,
    period: filters.value.period,
    dateFrom: filters.value.dateFrom,
    dateTo: filters.value.dateTo,
    currency: filters.value.currency,
  }),
  () => { void refresh() },
  { deep: true },
)

const summaryCurrency = computed(() => {
  const first = items.value[0]?.currency
  return first || organization.currentOrganization?.currency || 'MXN'
})
</script>

<template>
  <div class="transactions-page" data-testid="transactions-page">
    <AppPageHeader
      title="Movimientos"
      description="Ingresos, gastos, transferencias y ajustes."
    >
      <template #actions>
        <UiButton
          v-if="canWrite"
          class="hide-on-mobile"
          variant="primary"
          type="button"
          data-testid="transactions-new-button"
          @click="composer.openCreate('expense')"
        >
          + Nueva transacción
        </UiButton>
      </template>
    </AppPageHeader>

    <div class="transactions-page__summary">
      <MetricCard
        label="Ingresos (filtro)"
        :amount="summary.income"
        :currency="summaryCurrency"
      />
      <MetricCard
        label="Gastos (filtro)"
        :amount="summary.expense"
        :currency="summaryCurrency"
      />
      <MetricCard
        label="Neto cargado"
        :amount="summary.net"
        :currency="summaryCurrency"
      />
    </div>

    <UiCard class="transactions-page__filters">
      <TransactionFilters
        v-model="filters"
        :accounts="accounts"
        :categories="categories"
        @reset="resetFilters"
      />
    </UiCard>

    <UiAlert v-if="error" tone="danger" title="No se pudieron cargar los movimientos">
      <p>{{ error }}</p>
      <UiButton size="sm" type="button" style="margin-top: 0.75rem" @click="refresh">
        Reintentar
      </UiButton>
    </UiAlert>

    <p v-else class="transactions-page__count text-muted">
      {{ total }} movimiento{{ total === 1 ? '' : 's' }}
    </p>

    <UiCard v-if="showEmpty" class="transactions-page__empty" data-testid="transactions-empty">
      <UiEmptyState
        :title="emptyTitle"
        :description="emptyDescription"
      >
        <template #actions>
          <div class="transactions-page__empty-actions">
            <UiButton
              v-if="filtersActive"
              type="button"
              variant="secondary"
              data-testid="transactions-clear-filters"
              @click="resetFilters"
            >
              Limpiar filtros
            </UiButton>
            <UiButton
              v-else-if="filters.period !== 'all'"
              type="button"
              variant="secondary"
              data-testid="transactions-show-all-periods"
              @click="showAllPeriods"
            >
              Ver todo el historial
            </UiButton>
            <UiButton
              v-if="canWrite && !filtersActive"
              type="button"
              variant="primary"
              @click="composer.openCreate('expense')"
            >
              + Nueva transacción
            </UiButton>
          </div>
        </template>
      </UiEmptyState>
    </UiCard>

    <template v-else>
      <TransactionTable
        class="transactions-page__desktop"
        :items="items"
        :loading="loading"
      />

      <TransactionList
        class="transactions-page__mobile"
        :items="items"
        :loading="loading"
        :loading-more="loadingMore"
        :has-more="hasMore"
        :filters-active="filtersActive"
        @load-more="loadMore(filters)"
        @clear-filters="resetFilters"
      />
    </template>
  </div>
</template>

<style scoped>
.transactions-page {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding-bottom: var(--space-10);
}

.transactions-page__summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-3);
}

.transactions-page__count {
  margin: 0;
  font-size: 0.85rem;
}

.transactions-page__empty {
  padding: var(--space-4);
}

.transactions-page__empty-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  justify-content: center;
}

.transactions-page__mobile {
  display: none;
}

@media (max-width: 900px) {
  .transactions-page {
    padding-bottom: calc(var(--space-10) + 3.5rem);
  }

  .transactions-page__summary {
    grid-template-columns: 1fr;
  }

  .transactions-page__desktop {
    display: none;
  }

  .transactions-page__mobile {
    display: block;
  }
}
</style>
