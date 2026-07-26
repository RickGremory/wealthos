import type { ApiClient } from '~/lib/api/types'
import type {
  TimelineEventView,
  TimelineListQuery,
  TimelineListResult,
  TimelineSourceType,
  TimelineImportance,
} from '~/types/timeline'

interface TimelineEventDto {
  id: string
  organization_id: string
  occurred_at: string
  source_type: string
  event_type: string
  importance: string
  title: string
  description: string
  resource_type: string
  resource_id: string
  currency: string | null
  amount: string | number | null
  metadata?: Record<string, unknown>
  created_at?: string | null
}

interface TimelineListDto {
  items: TimelineEventDto[]
  next_cursor: string | null
  limit: number
}

function mapEvent(dto: TimelineEventDto): TimelineEventView {
  return {
    id: dto.id,
    organizationId: dto.organization_id,
    occurredAt: dto.occurred_at,
    sourceType: dto.source_type as TimelineSourceType,
    eventType: dto.event_type,
    importance: dto.importance as TimelineImportance,
    title: dto.title,
    description: dto.description,
    resourceType: dto.resource_type,
    resourceId: dto.resource_id,
    currency: dto.currency,
    amount: dto.amount == null ? null : String(dto.amount),
    metadata: dto.metadata ?? {},
  }
}

export function createTimelineRepository(api: ApiClient) {
  return {
    async list(
      organizationId: string,
      query: TimelineListQuery = {},
    ): Promise<TimelineListResult> {
      const params = new URLSearchParams()
      if (query.cursor) params.set('cursor', query.cursor)
      if (query.limit != null) params.set('limit', String(query.limit))
      if (query.sourceType) params.set('source_type', query.sourceType)
      if (query.importance) params.set('importance', query.importance)
      if (query.currency) params.set('currency', query.currency)
      if (query.dateFrom) params.set('date_from', query.dateFrom)
      if (query.dateTo) params.set('date_to', query.dateTo)
      const qs = params.toString()
      const dto = await api.get<TimelineListDto>(
        `/organizations/${organizationId}/timeline${qs ? `?${qs}` : ''}`,
      )
      return {
        items: (dto.items ?? []).map(mapEvent),
        nextCursor: dto.next_cursor,
        limit: dto.limit,
      }
    },
  }
}
