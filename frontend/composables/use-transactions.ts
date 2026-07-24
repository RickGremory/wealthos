import { createAccountsRepository } from '~/repositories/accounts.repository'
import { createCategoriesRepository } from '~/repositories/categories.repository'
import {
  createTransactionsRepository,
  enrichTransactionItem,
} from '~/repositories/transactions.repository'
import type {
  TransactionDetailView,
  TransactionListItemView,
  TransactionListQuery,
  TransactionNameMaps,
  UpdateTransactionMetadataInput,
} from '~/types/transactions'
import type { CategoryTreeNodeView } from '~/types/categories'
import type { AccountSummary } from '~/types/domain'
import { toUserMessage } from '~/lib/api/errors'
import { addDecimalStrings } from '~/utils/decimal-string'
import type { TransactionFiltersState } from '~/utils/transaction-filters'
import { resolvePeriodRange } from '~/utils/transaction-filters'

const PAGE_SIZE = 40

function flattenCategories(
  nodes: CategoryTreeNodeView[],
  parentName: string | null = null,
  map = new Map<string, { name: string, parentName?: string | null }>(),
) {
  for (const node of nodes) {
    map.set(node.id, { name: node.name, parentName })
    if (node.children?.length) {
      flattenCategories(node.children, node.name, map)
    }
  }
  return map
}

function buildNameMaps(
  accounts: AccountSummary[],
  categories: CategoryTreeNodeView[],
): TransactionNameMaps {
  const accountMap = new Map(
    accounts.map(a => [
      a.id,
      { name: a.name, currency: a.currency, accountType: a.accountType },
    ]),
  )
  return {
    accounts: accountMap,
    categories: flattenCategories(categories),
  }
}

export function filtersToListQuery(
  filters: TransactionFiltersState,
  pagination: { limit: number, offset: number },
): TransactionListQuery {
  const range = resolvePeriodRange(filters.period, filters.dateFrom, filters.dateTo)
  return {
    type: filters.type === 'all' ? null : filters.type,
    status: filters.status === 'all' ? null : filters.status,
    accountId: filters.accountId,
    categoryId: filters.categoryId,
    dateFrom: range.dateFrom,
    dateTo: range.dateTo,
    search: filters.search.trim() || null,
    limit: pagination.limit,
    offset: pagination.offset,
  }
}

export function useTransactions() {
  const organization = useOrganizationStore()
  const { $api } = useNuxtApp()
  const cache = useFinanceCache()

  const items = ref<TransactionListItemView[]>([])
  const total = ref(0)
  const offset = ref(0)
  const limit = ref(PAGE_SIZE)
  const loading = ref(false)
  const loadingMore = ref(false)
  const error = ref<string | null>(null)
  const accounts = ref<AccountSummary[]>([])
  const categories = ref<CategoryTreeNodeView[]>([])
  const nameMaps = ref<TransactionNameMaps>({})

  const hasMore = computed(() => items.value.length < total.value)

  const summary = computed(() => {
    const posted = items.value.filter(i => i.status === 'posted')
    const income = addDecimalStrings(
      ...posted.filter(i => i.type === 'income').map(i => i.amount.replace(/^[+-]/, '')),
      '0.00',
    )
    const expense = addDecimalStrings(
      ...posted.filter(i => i.type === 'expense').map(i => i.amount.replace(/^[+-]/, '')),
      '0.00',
    )
    return { income, expense, net: addDecimalStrings(income, `-${expense}`) }
  })

  async function loadEnrichment(orgId: string) {
    const accountsRepo = createAccountsRepository($api)
    const categoriesRepo = createCategoriesRepository($api)
    const [accountList, categoryTree] = await Promise.all([
      accountsRepo.list(orgId, { includeArchived: true }),
      categoriesRepo.list(orgId, { tree: true, includeArchived: true }),
    ])
    accounts.value = accountList
    categories.value = categoryTree
    nameMaps.value = buildNameMaps(accountList, categoryTree)
  }

  async function load(
    filters: TransactionFiltersState,
    options?: { reset?: boolean },
  ) {
    const orgId = organization.currentOrganizationId
    if (!orgId) {
      error.value = 'Selecciona una organización.'
      items.value = []
      return
    }

    const reset = options?.reset !== false
    if (reset) {
      offset.value = 0
      loading.value = true
    } else {
      loadingMore.value = true
    }
    error.value = null

    try {
      await loadEnrichment(orgId)
      const repo = createTransactionsRepository($api)
      const result = await repo.list(
        orgId,
        filtersToListQuery(filters, { limit: limit.value, offset: offset.value }),
        nameMaps.value,
      )
      const enriched = result.items.map(item =>
        enrichTransactionItem(item, nameMaps.value),
      )
      items.value = reset ? enriched : [...items.value, ...enriched]
      total.value = result.total
    } catch (e) {
      error.value = toUserMessage(e)
      if (reset) items.value = []
    } finally {
      loading.value = false
      loadingMore.value = false
    }
  }

  async function loadMore(filters: TransactionFiltersState) {
    if (!hasMore.value || loadingMore.value || loading.value) return
    offset.value += limit.value
    await load(filters, { reset: false })
  }

  async function getDetail(transactionId: string): Promise<TransactionDetailView | null> {
    const orgId = organization.currentOrganizationId
    if (!orgId) return null
    try {
      if (!nameMaps.value.accounts) {
        await loadEnrichment(orgId)
      }
      const repo = createTransactionsRepository($api)
      const detail = await repo.get(orgId, transactionId, nameMaps.value)
      return enrichTransactionItem(detail, nameMaps.value) as TransactionDetailView
    } catch (e) {
      error.value = toUserMessage(e)
      return null
    }
  }

  async function updateMetadata(
    transactionId: string,
    input: UpdateTransactionMetadataInput,
  ) {
    const orgId = organization.currentOrganizationId
    if (!orgId) throw new Error('no_org')
    const repo = createTransactionsRepository($api)
    const updated = await repo.updateMetadata(orgId, transactionId, input)
    cache.invalidateTransactions()
    return updated
  }

  async function voidTransaction(transactionId: string, reason: string) {
    const orgId = organization.currentOrganizationId
    if (!orgId) throw new Error('no_org')
    const repo = createTransactionsRepository($api)
    const notes = `Anulación: ${reason.trim()}`
    await repo.updateMetadata(orgId, transactionId, { notes })
    const voided = await repo.void(orgId, transactionId)
    cache.invalidateTransactions()
    return voided
  }

  function invalidate() {
    cache.invalidateTransactions()
  }

  watch(
    () => cache.transactionsVersion.value,
    () => {
      // Consumers should re-call load with their filters; version bump signals freshness.
    },
  )

  return {
    items,
    total,
    offset,
    limit,
    loading,
    loadingMore,
    error,
    accounts,
    categories,
    nameMaps,
    hasMore,
    summary,
    load,
    loadMore,
    getDetail,
    updateMetadata,
    voidTransaction,
    invalidate,
    loadEnrichment,
  }
}
