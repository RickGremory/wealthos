import type { TransactionFiltersState } from '~/types/transactions'
import {
  emptyTransactionFilters,
  filtersFromQuery,
  filtersToQuery,
  resolvePeriodRange,
} from '~/utils/transaction-filters'

function queryKey(query: Record<string, string>): string {
  return Object.keys(query)
    .sort()
    .map(k => `${k}=${query[k]}`)
    .join('&')
}

export function useTransactionFilters() {
  const route = useRoute()
  const router = useRouter()

  const filters = ref<TransactionFiltersState>(
    filtersFromQuery(route.query as Record<string, unknown>),
  )

  const resolvedRange = computed(() =>
    resolvePeriodRange(filters.value.period, filters.value.dateFrom, filters.value.dateTo),
  )

  const syncingFromRoute = ref(false)

  function applyFilters(next: Partial<TransactionFiltersState>) {
    filters.value = { ...filters.value, ...next }
  }

  function resetFilters() {
    filters.value = emptyTransactionFilters()
  }

  async function syncToRoute() {
    const query = filtersToQuery(filters.value)
    if (queryKey(query) === queryKey(route.query as Record<string, string>)) return
    syncingFromRoute.value = true
    try {
      await router.replace({ query })
    } finally {
      // allow route watcher to settle
      await nextTick()
      syncingFromRoute.value = false
    }
  }

  watch(
    () => route.query,
    (query) => {
      if (syncingFromRoute.value) return
      const next = filtersFromQuery(query as Record<string, unknown>)
      if (queryKey(filtersToQuery(next)) === queryKey(filtersToQuery(filters.value))) return
      filters.value = next
    },
  )

  watch(
    filters,
    () => {
      if (syncingFromRoute.value) return
      void syncToRoute()
    },
    { deep: true },
  )

  return {
    filters,
    resolvedRange,
    applyFilters,
    resetFilters,
    syncToRoute,
  }
}
