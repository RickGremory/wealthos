import { createCommitmentsRepository } from '~/repositories/commitments.repository'
import type {
  CommitmentListItemView,
  CommitmentStatusFilter,
  CommitmentSummaryView,
  CommitmentStrategyView,
} from '~/types/commitments'
import { toUserMessage } from '~/lib/api/errors'
import { isAttentionStatus } from '~/utils/commitment-status'
import { sortCommitments } from '~/utils/commitment-sort'

const emptySummary = (): CommitmentSummaryView => ({
  groups: [],
  activeCommitments: 0,
  commitmentsNeedingAttention: 0,
  nextDue: null,
})

export function useCommitments() {
  const organization = useOrganizationStore()
  const { $api } = useNuxtApp()
  const cache = useFinanceCache()

  const items = ref<CommitmentListItemView[]>([])
  const summary = ref<CommitmentSummaryView>(emptySummary())
  const strategy = ref<CommitmentStrategyView | null>(null)
  const listLoading = ref(false)
  const summaryLoading = ref(false)
  const strategyLoading = ref(false)
  const listError = ref<string | null>(null)
  const summaryError = ref<string | null>(null)
  const strategyError = ref<string | null>(null)
  const statusFilter = ref<CommitmentStatusFilter>('all')
  const includeArchived = ref(false)

  const sortedItems = computed(() => sortCommitments(items.value))

  const visibleItems = computed(() => {
    let list = sortedItems.value
    if (!includeArchived.value) {
      list = list.filter(i => i.status !== 'archived')
    }
    switch (statusFilter.value) {
      case 'attention':
        return list.filter(i => isAttentionStatus(i.displayStatus))
      case 'active':
        return list.filter(i => i.status === 'active')
      case 'paused':
        return list.filter(i => i.status === 'paused')
      case 'closed':
        return list.filter(i => i.status === 'closed')
      case 'archived':
        return list.filter(i => i.status === 'archived')
      default:
        return list
    }
  })

  const hasAny = computed(() => items.value.length > 0)
  const hasActive = computed(() => items.value.some(i => i.status === 'active'))
  const attentionItems = computed(() =>
    sortedItems.value.filter(i => isAttentionStatus(i.displayStatus)),
  )

  async function loadList() {
    const orgId = organization.currentOrganizationId
    if (!orgId) {
      listError.value = 'Selecciona una organización.'
      items.value = []
      return
    }
    listLoading.value = true
    listError.value = null
    try {
      const repo = createCommitmentsRepository($api)
      items.value = await repo.list(orgId, { includeArchived: true })
    }
    catch (e) {
      listError.value = toUserMessage(e)
      items.value = []
    }
    finally {
      listLoading.value = false
    }
  }

  async function loadSummary() {
    const orgId = organization.currentOrganizationId
    if (!orgId) {
      summary.value = emptySummary()
      summaryError.value = null
      return
    }
    summaryLoading.value = true
    summaryError.value = null
    try {
      const repo = createCommitmentsRepository($api)
      summary.value = await repo.summary(orgId)
    }
    catch (e) {
      summary.value = emptySummary()
      summaryError.value = toUserMessage(e)
    }
    finally {
      summaryLoading.value = false
    }
  }

  async function loadStrategy() {
    const orgId = organization.currentOrganizationId
    if (!orgId) {
      strategy.value = null
      return
    }
    strategyLoading.value = true
    strategyError.value = null
    try {
      const repo = createCommitmentsRepository($api)
      strategy.value = await repo.getStrategy(orgId)
    }
    catch (e) {
      strategyError.value = toUserMessage(e)
      strategy.value = null
    }
    finally {
      strategyLoading.value = false
    }
  }

  async function load() {
    await Promise.all([loadList(), loadSummary(), loadStrategy()])
  }

  watch(
    () => cache.commitmentsVersion.value,
    () => {
      void load()
    },
  )

  return {
    items,
    sortedItems,
    visibleItems,
    attentionItems,
    summary,
    strategy,
    listLoading,
    summaryLoading,
    strategyLoading,
    listError,
    summaryError,
    strategyError,
    statusFilter,
    includeArchived,
    hasAny,
    hasActive,
    load,
    loadList,
    loadSummary,
    loadStrategy,
  }
}
