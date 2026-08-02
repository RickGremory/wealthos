import { createRecurringRepository } from '~/repositories/recurring.repository'
import type {
  RecurringDirectionFilter,
  RecurringOccurrenceStatus,
  RecurringOccurrenceView,
  RecurringRuleListItemView,
  RecurringStatusFilter,
} from '~/types/recurring'
import { toUserMessage } from '~/lib/api/errors'
import { todayLocalIsoDate } from '~/composables/use-date'

const ATTENTION_STATUSES: RecurringOccurrenceStatus[] = ['due', 'overdue', 'partially_settled']

export function useRecurring() {
  const organization = useOrganizationStore()
  const { $api } = useNuxtApp()
  const cache = useFinanceCache()

  const rules = ref<RecurringRuleListItemView[]>([])
  const occurrences = ref<RecurringOccurrenceView[]>([])
  const listLoading = ref(false)
  const occurrencesLoading = ref(false)
  const listError = ref<string | null>(null)
  const occurrencesError = ref<string | null>(null)
  const statusFilter = ref<RecurringStatusFilter>('all')
  const directionFilter = ref<RecurringDirectionFilter>('all')
  const includeArchived = ref(false)

  const visibleRules = computed(() => {
    let list = rules.value
    if (!includeArchived.value) {
      list = list.filter(item => item.status !== 'archived')
    }
    if (directionFilter.value !== 'all') {
      list = list.filter(item => item.direction === directionFilter.value)
    }
    switch (statusFilter.value) {
      case 'active':
        return list.filter(item => item.status === 'active')
      case 'paused':
        return list.filter(item => item.status === 'paused')
      case 'ended':
        return list.filter(item => item.status === 'ended')
      case 'archived':
        return list.filter(item => item.status === 'archived')
      case 'attention':
        return list.filter((item) => {
          const status = item.nextOccurrence?.status
          return status != null && ATTENTION_STATUSES.includes(status)
        })
      default:
        return list
    }
  })

  const attentionOccurrences = computed(() =>
    occurrences.value.filter(item => ATTENTION_STATUSES.includes(item.status)),
  )

  const upcomingOccurrences = computed(() =>
    occurrences.value.filter(item =>
      item.status === 'upcoming' || item.status === 'due',
    ),
  )

  const summaryByCurrency = computed(() => {
    const map = new Map<string, { currency: string, inflow: number, outflow: number, upcoming: number, pending: number }>()
    for (const item of occurrences.value) {
      const row = map.get(item.currency) ?? {
        currency: item.currency,
        inflow: 0,
        outflow: 0,
        upcoming: 0,
        pending: 0,
      }
      const amount = Number(item.expectedAmount)
      if (item.direction === 'inflow') row.inflow += amount
      if (item.direction === 'outflow') row.outflow += amount
      if (item.status === 'upcoming' || item.status === 'due') row.upcoming += 1
      if (ATTENTION_STATUSES.includes(item.status)) row.pending += 1
      map.set(item.currency, row)
    }
    return [...map.values()]
  })

  const hasAny = computed(() => rules.value.length > 0)

  async function loadRules() {
    const orgId = organization.currentOrganizationId
    if (!orgId) {
      listError.value = 'Selecciona una organización.'
      rules.value = []
      return
    }
    listLoading.value = true
    listError.value = null
    try {
      const repo = createRecurringRepository($api)
      rules.value = await repo.list(orgId, { includeArchived: true })
    }
    catch (e) {
      listError.value = toUserMessage(e)
      rules.value = []
    }
    finally {
      listLoading.value = false
    }
  }

  async function loadOccurrences() {
    const orgId = organization.currentOrganizationId
    if (!orgId) {
      occurrences.value = []
      return
    }
    occurrencesLoading.value = true
    occurrencesError.value = null
    try {
      const from = todayLocalIsoDate()
      const toAnchor = new Date()
      toAnchor.setDate(toAnchor.getDate() + 45)
      const past = new Date()
      past.setDate(past.getDate() - 14)
      const repo = createRecurringRepository($api)
      occurrences.value = await repo.listOccurrences(orgId, {
        from: todayLocalIsoDate(past),
        to: todayLocalIsoDate(toAnchor),
      })
    }
    catch (e) {
      occurrencesError.value = toUserMessage(e)
      occurrences.value = []
    }
    finally {
      occurrencesLoading.value = false
    }
  }

  async function load() {
    await Promise.all([loadRules(), loadOccurrences()])
  }

  watch(
    () => cache.recurringVersion.value,
    () => {
      void load()
    },
  )

  return {
    rules,
    occurrences,
    visibleRules,
    attentionOccurrences,
    upcomingOccurrences,
    summaryByCurrency,
    listLoading,
    occurrencesLoading,
    listError,
    occurrencesError,
    statusFilter,
    directionFilter,
    includeArchived,
    hasAny,
    load,
    loadRules,
    loadOccurrences,
  }
}
