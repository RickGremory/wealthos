<script setup lang="ts">
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

async function refresh() {
  await load(filters.value, { reset: true })
}

onMounted(async () => {
  await refresh()
  if (route.query.new === '1' || route.query.new === 'true') {
    composer.openCreate('expense')
    // clear query without reload noise
    const { new: _drop, ...rest } = route.query
    void navigateTo({ query: rest }, { replace: true })
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
      @load-more="loadMore(filters)"
    />
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
