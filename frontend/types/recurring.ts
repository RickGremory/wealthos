export type RecurringDirection = 'inflow' | 'outflow' | 'transfer'
export type RecurringRuleStatus = 'active' | 'paused' | 'ended' | 'archived'
export type RecurringSourceType =
  | 'manual'
  | 'commitment'
  | 'goal'
  | 'tax'
  | 'system'
  | 'imported'
export type RecurringFrequency = 'daily' | 'weekly' | 'monthly' | 'yearly'
export type RecurringCertainty = 'confirmed' | 'expected' | 'estimated'
export type RecurringAmountStrategy = 'fixed' | 'estimated'
export type RecurringSettlementMode = 'single_transaction' | 'cumulative'
export type RecurringOccurrenceStatus =
  | 'upcoming'
  | 'due'
  | 'overdue'
  | 'settled'
  | 'partially_settled'
  | 'skipped'
  | 'cancelled'
export type RecurringExceptionType =
  | 'skip'
  | 'reschedule'
  | 'amount_override'
  | 'override'
export type InvalidDatePolicy = 'last_day_of_month' | 'skip_occurrence'

export interface RecurrencePatternInput {
  frequency: RecurringFrequency
  interval: number
  daysOfWeek?: number[]
  dayOfMonth?: number | null
  monthOfYear?: number | null
  endOfMonth?: boolean
  invalidDatePolicy?: InvalidDatePolicy
}

export interface RecurringOccurrenceView {
  occurrenceKey: string
  recurringRuleId: string
  originalExpectedOn: string
  expectedOn: string
  expectedAt: string
  direction: RecurringDirection
  baseAmount: string
  expectedAmount: string
  currency: string
  certainty: RecurringCertainty
  status: RecurringOccurrenceStatus
  isException: boolean
  exceptionType: RecurringExceptionType | null
  name: string
  accountId: string | null
  destinationAccountId: string | null
  categoryId: string | null
  actualAmount: string | null
  varianceAmount: string | null
  canConfirm: boolean
  canSkip: boolean
  canReschedule: boolean
}

export interface RecurringVersionView {
  id: string
  effectiveFrom: string
  effectiveUntil: string | null
  name: string
  direction: RecurringDirection
  amount: string
  currency: string
  frequency: RecurringFrequency
  interval: number
  dayOfMonth: number | null
  endOfMonth: boolean
  daysOfWeek: number[]
  monthOfYear: number | null
  invalidDatePolicy: InvalidDatePolicy
  startsOn: string
  endsOn: string | null
  gracePeriodDays: number
  amountStrategy: RecurringAmountStrategy
  certainty: RecurringCertainty
  settlementMode: RecurringSettlementMode
  accountId: string | null
  destinationAccountId: string | null
  categoryId: string | null
  notes: string | null
}

export interface RecurringRuleListItemView {
  id: string
  name: string
  direction: RecurringDirection
  amount: string
  currency: string
  status: RecurringRuleStatus
  sourceType: RecurringSourceType
  isManagedExternally: boolean
  frequency: RecurringFrequency
  interval: number
  scheduleLabel: string
  version: number
  nextOccurrence: RecurringOccurrenceView | null
}

export interface RecurringRuleDetailView {
  id: string
  name: string
  direction: RecurringDirection
  amount: string
  currency: string
  status: RecurringRuleStatus
  sourceType: RecurringSourceType
  isManagedExternally: boolean
  relatedResourceType: string | null
  relatedResourceId: string | null
  version: number
  createdAt: string
  updatedAt: string
  archivedAt: string | null
  currentVersion: RecurringVersionView
  versions: RecurringVersionView[]
  upcomingOccurrences: RecurringOccurrenceView[]
  notes: string | null
}

export interface RecurringPreviewView {
  dates: string[]
  occurrences: RecurringOccurrenceView[]
}

export interface RecurringCalendarEventView {
  id: string
  recurringRuleId: string
  name: string
  eventType: string
  eventDate: string
  severity: string
  currency: string
  direction: RecurringDirection
  amount: string
  occurrenceKey: string
  status: string
}

export interface CreateRecurringRuleInput {
  name: string
  direction: RecurringDirection
  amount: string
  currency: string
  pattern: RecurrencePatternInput
  startsOn: string
  endsOn?: string | null
  amountStrategy?: RecurringAmountStrategy
  certainty?: RecurringCertainty
  settlementMode?: RecurringSettlementMode
  accountId?: string | null
  destinationAccountId?: string | null
  categoryId?: string | null
  gracePeriodDays?: number
  notes?: string | null
}

export interface RecurringPreviewInput {
  name?: string
  direction?: RecurringDirection
  amount?: string
  currency?: string
  pattern: RecurrencePatternInput
  startsOn: string
  endsOn?: string | null
  from: string
  to: string
  amountStrategy?: RecurringAmountStrategy
  certainty?: RecurringCertainty
  gracePeriodDays?: number
}

export interface CreateExceptionInput {
  occurrenceKey: string
  exceptionType: RecurringExceptionType
  expectedVersion: number
  replacementExpectedOn?: string | null
  replacementAmount?: string | null
  replacementCertainty?: RecurringCertainty | null
  reason?: string | null
}

export interface RecurringFormModel {
  name: string
  direction: RecurringDirection
  amount: string
  currency: string
  frequency: RecurringFrequency
  interval: number
  dayOfMonth: number | null
  endOfMonth: boolean
  daysOfWeek: number[]
  monthOfYear: number | null
  invalidDatePolicy: InvalidDatePolicy
  startsOn: string
  endsOn: string
  accountId: string
  destinationAccountId: string
  categoryId: string
  certainty: RecurringCertainty
  notes: string
}

export type RecurringStatusFilter =
  | 'all'
  | 'active'
  | 'paused'
  | 'ended'
  | 'archived'
  | 'attention'

export type RecurringDirectionFilter = 'all' | RecurringDirection
