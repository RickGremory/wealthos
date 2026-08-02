export type TimelineSourceType =
  | 'transaction'
  | 'goal'
  | 'commitment'
  | 'planning'
  | 'tax'
  | 'system'
  | 'recurring'

export type TimelineImportance = 'low' | 'normal' | 'high' | 'critical'

export interface TimelineEventView {
  id: string
  organizationId: string
  occurredAt: string
  sourceType: TimelineSourceType
  eventType: string
  importance: TimelineImportance
  title: string
  description: string
  resourceType: string
  resourceId: string
  currency: string | null
  amount: string | null
  metadata: Record<string, unknown>
}

export interface TimelineListResult {
  items: TimelineEventView[]
  nextCursor: string | null
  limit: number
}

export interface TimelineListQuery {
  cursor?: string | null
  limit?: number
  sourceType?: TimelineSourceType | null
  importance?: TimelineImportance | null
  currency?: string | null
  dateFrom?: string | null
  dateTo?: string | null
}
