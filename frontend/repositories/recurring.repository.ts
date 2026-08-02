import type { ApiClient } from '~/lib/api/types'
import type {
  CreateExceptionInput,
  CreateRecurringRuleInput,
  RecurrencePatternInput,
  RecurringCalendarEventView,
  RecurringOccurrenceView,
  RecurringPreviewInput,
  RecurringPreviewView,
  RecurringRuleDetailView,
  RecurringRuleListItemView,
  RecurringVersionView,
} from '~/types/recurring'

interface OccurrenceDto {
  occurrence_key: string
  recurring_rule_id: string
  original_expected_on: string
  expected_on: string
  expected_at: string
  direction: string
  base_amount: string
  expected_amount: string
  currency: string
  certainty: string
  status: string
  is_exception: boolean
  exception_type: string | null
  name: string
  account_id: string | null
  destination_account_id: string | null
  category_id: string | null
  actual_amount: string | null
  variance_amount: string | null
  can_confirm: boolean
  can_skip: boolean
  can_reschedule: boolean
}

interface VersionDto {
  id: string
  effective_from: string
  effective_until: string | null
  name: string
  direction: string
  amount: string
  currency: string
  frequency: string
  interval: number
  day_of_month: number | null
  end_of_month: boolean
  days_of_week: number[]
  month_of_year: number | null
  invalid_date_policy: string
  starts_on: string
  ends_on: string | null
  grace_period_days: number
  amount_strategy: string
  certainty: string
  settlement_mode: string
  account_id: string | null
  destination_account_id: string | null
  category_id: string | null
  notes: string | null
}

interface RuleListDto {
  id: string
  name: string
  direction: string
  amount: string
  currency: string
  status: string
  source_type: string
  is_managed_externally: boolean
  frequency: string
  interval: number
  schedule_label: string
  version: number
  next_occurrence: OccurrenceDto | null
}

interface RuleDetailDto {
  id: string
  name: string
  direction: string
  amount: string
  currency: string
  status: string
  source_type: string
  is_managed_externally: boolean
  related_resource_type: string | null
  related_resource_id: string | null
  version: number
  created_at: string
  updated_at: string
  archived_at: string | null
  current_version: VersionDto
  versions: VersionDto[]
  upcoming_occurrences: OccurrenceDto[]
  notes: string | null
}

function mapOccurrence(dto: OccurrenceDto): RecurringOccurrenceView {
  return {
    occurrenceKey: dto.occurrence_key,
    recurringRuleId: dto.recurring_rule_id,
    originalExpectedOn: dto.original_expected_on,
    expectedOn: dto.expected_on,
    expectedAt: dto.expected_at,
    direction: dto.direction as RecurringOccurrenceView['direction'],
    baseAmount: String(dto.base_amount),
    expectedAmount: String(dto.expected_amount),
    currency: dto.currency,
    certainty: dto.certainty as RecurringOccurrenceView['certainty'],
    status: dto.status as RecurringOccurrenceView['status'],
    isException: dto.is_exception,
    exceptionType: (dto.exception_type as RecurringOccurrenceView['exceptionType']) ?? null,
    name: dto.name,
    accountId: dto.account_id,
    destinationAccountId: dto.destination_account_id,
    categoryId: dto.category_id,
    actualAmount: dto.actual_amount != null ? String(dto.actual_amount) : null,
    varianceAmount: dto.variance_amount != null ? String(dto.variance_amount) : null,
    canConfirm: dto.can_confirm,
    canSkip: dto.can_skip,
    canReschedule: dto.can_reschedule,
  }
}

function mapVersion(dto: VersionDto): RecurringVersionView {
  return {
    id: dto.id,
    effectiveFrom: dto.effective_from,
    effectiveUntil: dto.effective_until,
    name: dto.name,
    direction: dto.direction as RecurringVersionView['direction'],
    amount: String(dto.amount),
    currency: dto.currency,
    frequency: dto.frequency as RecurringVersionView['frequency'],
    interval: dto.interval,
    dayOfMonth: dto.day_of_month,
    endOfMonth: dto.end_of_month,
    daysOfWeek: dto.days_of_week ?? [],
    monthOfYear: dto.month_of_year,
    invalidDatePolicy: dto.invalid_date_policy as RecurringVersionView['invalidDatePolicy'],
    startsOn: dto.starts_on,
    endsOn: dto.ends_on,
    gracePeriodDays: dto.grace_period_days,
    amountStrategy: dto.amount_strategy as RecurringVersionView['amountStrategy'],
    certainty: dto.certainty as RecurringVersionView['certainty'],
    settlementMode: dto.settlement_mode as RecurringVersionView['settlementMode'],
    accountId: dto.account_id,
    destinationAccountId: dto.destination_account_id,
    categoryId: dto.category_id,
    notes: dto.notes,
  }
}

function mapListItem(dto: RuleListDto): RecurringRuleListItemView {
  return {
    id: dto.id,
    name: dto.name,
    direction: dto.direction as RecurringRuleListItemView['direction'],
    amount: String(dto.amount),
    currency: dto.currency,
    status: dto.status as RecurringRuleListItemView['status'],
    sourceType: dto.source_type as RecurringRuleListItemView['sourceType'],
    isManagedExternally: dto.is_managed_externally,
    frequency: dto.frequency as RecurringRuleListItemView['frequency'],
    interval: dto.interval,
    scheduleLabel: dto.schedule_label,
    version: dto.version,
    nextOccurrence: dto.next_occurrence ? mapOccurrence(dto.next_occurrence) : null,
  }
}

function mapDetail(dto: RuleDetailDto): RecurringRuleDetailView {
  return {
    id: dto.id,
    name: dto.name,
    direction: dto.direction as RecurringRuleDetailView['direction'],
    amount: String(dto.amount),
    currency: dto.currency,
    status: dto.status as RecurringRuleDetailView['status'],
    sourceType: dto.source_type as RecurringRuleDetailView['sourceType'],
    isManagedExternally: dto.is_managed_externally,
    relatedResourceType: dto.related_resource_type,
    relatedResourceId: dto.related_resource_id,
    version: dto.version,
    createdAt: dto.created_at,
    updatedAt: dto.updated_at,
    archivedAt: dto.archived_at,
    currentVersion: mapVersion(dto.current_version),
    versions: (dto.versions ?? []).map(mapVersion),
    upcomingOccurrences: (dto.upcoming_occurrences ?? []).map(mapOccurrence),
    notes: dto.notes,
  }
}

function patternToApi(pattern: RecurrencePatternInput): Record<string, unknown> {
  const body: Record<string, unknown> = {
    frequency: pattern.frequency,
    interval: pattern.interval,
  }
  if (pattern.frequency === 'weekly') {
    body.days_of_week = pattern.daysOfWeek ?? []
  }
  if (pattern.frequency === 'monthly' || pattern.frequency === 'yearly') {
    body.end_of_month = Boolean(pattern.endOfMonth)
    body.day_of_month = pattern.endOfMonth ? null : pattern.dayOfMonth ?? null
    body.invalid_date_policy = pattern.invalidDatePolicy ?? 'last_day_of_month'
  }
  if (pattern.frequency === 'yearly') {
    body.month_of_year = pattern.monthOfYear
  }
  return body
}

function base(orgId: string) {
  return `/organizations/${orgId}/recurring`
}

export function createRecurringRepository(api: ApiClient) {
  return {
    async list(
      organizationId: string,
      params?: {
        status?: string
        direction?: string
        currency?: string
        includeArchived?: boolean
      },
    ): Promise<RecurringRuleListItemView[]> {
      const qs = new URLSearchParams()
      if (params?.status) qs.set('status', params.status)
      if (params?.direction) qs.set('direction', params.direction)
      if (params?.currency) qs.set('currency', params.currency)
      if (params?.includeArchived) qs.set('include_archived', 'true')
      const suffix = qs.toString() ? `?${qs}` : ''
      const rows = await api.get<RuleListDto[]>(`${base(organizationId)}${suffix}`)
      return rows.map(mapListItem)
    },

    async get(organizationId: string, ruleId: string): Promise<RecurringRuleDetailView> {
      const dto = await api.get<RuleDetailDto>(`${base(organizationId)}/${ruleId}`)
      return mapDetail(dto)
    },

    async create(
      organizationId: string,
      input: CreateRecurringRuleInput,
    ): Promise<RecurringRuleDetailView> {
      const dto = await api.post<RuleDetailDto>(base(organizationId), {
        name: input.name,
        direction: input.direction,
        amount: input.amount,
        currency: input.currency,
        pattern: patternToApi(input.pattern),
        starts_on: input.startsOn,
        ends_on: input.endsOn ?? null,
        amount_strategy: input.amountStrategy ?? 'fixed',
        certainty: input.certainty ?? 'expected',
        settlement_mode: input.settlementMode ?? 'single_transaction',
        account_id: input.accountId ?? null,
        destination_account_id: input.destinationAccountId ?? null,
        category_id: input.categoryId ?? null,
        grace_period_days: input.gracePeriodDays ?? 0,
        notes: input.notes ?? null,
      })
      return mapDetail(dto)
    },

    async preview(
      organizationId: string,
      input: RecurringPreviewInput,
    ): Promise<RecurringPreviewView> {
      const dto = await api.post<{ dates: string[], occurrences: OccurrenceDto[] }>(
        `${base(organizationId)}/preview`,
        {
          name: input.name ?? 'Preview',
          direction: input.direction ?? 'outflow',
          amount: input.amount ?? '1.00',
          currency: input.currency ?? 'MXN',
          pattern: patternToApi(input.pattern),
          starts_on: input.startsOn,
          ends_on: input.endsOn ?? null,
          from: input.from,
          to: input.to,
          amount_strategy: input.amountStrategy ?? 'fixed',
          certainty: input.certainty ?? 'expected',
          grace_period_days: input.gracePeriodDays ?? 0,
        },
      )
      return {
        dates: dto.dates,
        occurrences: (dto.occurrences ?? []).map(mapOccurrence),
      }
    },

    async listOccurrences(
      organizationId: string,
      params: {
        from: string
        to: string
        currency?: string
        status?: string
        ruleId?: string
      },
    ): Promise<RecurringOccurrenceView[]> {
      const qs = new URLSearchParams({ from: params.from, to: params.to })
      if (params.currency) qs.set('currency', params.currency)
      if (params.status) qs.set('status', params.status)
      if (params.ruleId) qs.set('rule_id', params.ruleId)
      const rows = await api.get<OccurrenceDto[]>(
        `${base(organizationId)}/occurrences?${qs}`,
      )
      return rows.map(mapOccurrence)
    },

    async calendarEvents(
      organizationId: string,
      params?: { dateFrom?: string, dateTo?: string, currency?: string },
    ): Promise<RecurringCalendarEventView[]> {
      const qs = new URLSearchParams()
      if (params?.dateFrom) qs.set('from', params.dateFrom)
      if (params?.dateTo) qs.set('to', params.dateTo)
      if (params?.currency) qs.set('currency', params.currency)
      const suffix = qs.toString() ? `?${qs}` : ''
      const dto = await api.get<{ items: Array<Record<string, unknown>> }>(
        `${base(organizationId)}/calendar-events${suffix}`,
      )
      return (dto.items ?? []).map(item => ({
        id: String(item.id),
        recurringRuleId: String(item.recurring_rule_id),
        name: String(item.name),
        eventType: String(item.event_type),
        eventDate: String(item.event_date),
        severity: String(item.severity),
        currency: String(item.currency),
        direction: item.direction as RecurringCalendarEventView['direction'],
        amount: String(item.amount),
        occurrenceKey: String(item.occurrence_key),
        status: String(item.status),
      }))
    },

    async pause(
      organizationId: string,
      ruleId: string,
      body: { startsOn: string, endsOn?: string | null, expectedVersion: number, reason?: string },
    ): Promise<RecurringRuleDetailView> {
      const dto = await api.post<RuleDetailDto>(`${base(organizationId)}/${ruleId}/pause`, {
        starts_on: body.startsOn,
        ends_on: body.endsOn ?? null,
        expected_version: body.expectedVersion,
        reason: body.reason ?? null,
      })
      return mapDetail(dto)
    },

    async resume(
      organizationId: string,
      ruleId: string,
      body: { resumeOn: string, expectedVersion: number },
    ): Promise<RecurringRuleDetailView> {
      const dto = await api.post<RuleDetailDto>(`${base(organizationId)}/${ruleId}/resume`, {
        resume_on: body.resumeOn,
        expected_version: body.expectedVersion,
      })
      return mapDetail(dto)
    },

    async end(
      organizationId: string,
      ruleId: string,
      body: { endsOn: string, expectedVersion: number },
    ): Promise<RecurringRuleDetailView> {
      const dto = await api.post<RuleDetailDto>(`${base(organizationId)}/${ruleId}/end`, {
        ends_on: body.endsOn,
        expected_version: body.expectedVersion,
      })
      return mapDetail(dto)
    },

    async archive(
      organizationId: string,
      ruleId: string,
      expectedVersion: number,
    ): Promise<RecurringRuleDetailView> {
      const dto = await api.post<RuleDetailDto>(`${base(organizationId)}/${ruleId}/archive`, {
        expected_version: expectedVersion,
      })
      return mapDetail(dto)
    },

    async createException(
      organizationId: string,
      ruleId: string,
      input: CreateExceptionInput,
    ): Promise<RecurringRuleDetailView> {
      const dto = await api.post<RuleDetailDto>(
        `${base(organizationId)}/${ruleId}/exceptions`,
        {
          occurrence_key: input.occurrenceKey,
          exception_type: input.exceptionType,
          expected_version: input.expectedVersion,
          replacement_expected_on: input.replacementExpectedOn ?? null,
          replacement_amount: input.replacementAmount ?? null,
          replacement_certainty: input.replacementCertainty ?? null,
          reason: input.reason ?? null,
        },
      )
      return mapDetail(dto)
    },
  }
}
