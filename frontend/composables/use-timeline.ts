import { createTimelineRepository } from '~/repositories/timeline.repository'
import type { TimelineEventView, TimelineSourceType } from '~/types/timeline'
import { toUserMessage } from '~/lib/api/errors'

export function useTimeline() {
  const organization = useOrganizationStore()
  const preferences = usePreferencesStore()
  const { $api } = useNuxtApp()

  const items = ref<TimelineEventView[]>([])
  const nextCursor = ref<string | null>(null)
  const loading = ref(false)
  const loadingMore = ref(false)
  const error = ref<string | null>(null)
  const sourceFilter = ref<TimelineSourceType | ''>('')

  async function load(reset = true) {
    const orgId = organization.currentOrganizationId
    if (!orgId) return

    if (reset) {
      loading.value = true
      nextCursor.value = null
      items.value = []
    }
    else {
      loadingMore.value = true
    }
    error.value = null

    const currency = preferences.preferredDashboardCurrency
      || organization.currentOrganization?.currency
      || null

    try {
      const repo = createTimelineRepository($api)
      const result = await repo.list(orgId, {
        limit: 40,
        cursor: reset ? null : nextCursor.value,
        sourceType: sourceFilter.value || null,
        currency,
      })
      items.value = reset ? result.items : [...items.value, ...result.items]
      nextCursor.value = result.nextCursor
    }
    catch (e) {
      error.value = toUserMessage(e)
    }
    finally {
      loading.value = false
      loadingMore.value = false
    }
  }

  async function loadMore() {
    if (!nextCursor.value || loadingMore.value) return
    await load(false)
  }

  const groupedByDay = computed(() => {
    const groups = new Map<string, TimelineEventView[]>()
    for (const item of items.value) {
      const day = item.occurredAt.slice(0, 10)
      const list = groups.get(day) ?? []
      list.push(item)
      groups.set(day, list)
    }
    return [...groups.entries()].map(([day, events]) => ({ day, events }))
  })

  return {
    items,
    groupedByDay,
    nextCursor,
    loading,
    loadingMore,
    error,
    sourceFilter,
    load,
    loadMore,
  }
}

export function timelineResourcePath(event: TimelineEventView): string | null {
  if (event.resourceType === 'transaction') {
    return `/app/transactions/${event.resourceId}`
  }
  if (event.resourceType === 'goal') {
    return `/app/goals/${event.resourceId}`
  }
  if (event.resourceType === 'commitment') {
    return `/app/commitments/${event.resourceId}`
  }
  if (event.resourceType === 'recurring_rule') {
    return `/app/recurring/${event.resourceId}`
  }
  return null
}
