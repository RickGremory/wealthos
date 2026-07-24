import type { ApiClient } from '~/lib/api/types'
import type {
  CreateGoalInput,
  GoalDetailView,
  GoalListItemView,
  GoalPriority,
  GoalStatus,
  GoalStrategy,
  UpdateGoalInput,
} from '~/types/goals'
import { deriveGoalDisplayStatus } from '~/utils/goal-status'
import { toGoalPriority } from '~/utils/goal-priority'

interface GoalDto {
  id: string
  organization_id: string
  name: string
  target_amount: string | number
  currency: string
  target_date: string | null
  strategy: string
  linked_account_ids: string[]
  status: string
  current_amount: string | number
  remaining_amount: string | number
  completion_percentage: string | number
  estimated_completion_date: string | null
  created_at: string
  updated_at: string
  completed_at: string | null
  archived_at: string | null
}

interface GoalListDto {
  items: GoalDto[]
  total: number
}

function toDecimalString(value: string | number | null | undefined): string {
  if (value == null) return '0.00'
  if (typeof value === 'number') {
    return value.toFixed(2)
  }
  const trimmed = String(value).trim()
  return trimmed || '0.00'
}

function toPercentString(value: string | number | null | undefined): string {
  if (value == null) return '0'
  if (typeof value === 'number') {
    return String(value)
  }
  return String(value).trim() || '0'
}

/** @internal Exported for unit tests. */
export function mapGoalDto(
  dto: GoalDto,
  priority: GoalPriority = 2,
): GoalListItemView {
  const status = (dto.status as GoalStatus) || 'active'
  const targetAmount = toDecimalString(dto.target_amount)
  const currentAmount = toDecimalString(dto.current_amount)
  const remainingAmount = toDecimalString(dto.remaining_amount)
  const completionPercentage = toPercentString(dto.completion_percentage)

  const display = deriveGoalDisplayStatus({
    status,
    targetDate: dto.target_date,
    estimatedCompletionDate: dto.estimated_completion_date,
    completionPercentage,
  })

  return {
    id: dto.id,
    organizationId: dto.organization_id,
    name: dto.name,
    targetAmount,
    currency: dto.currency,
    targetDate: dto.target_date,
    strategy: dto.strategy as GoalStrategy,
    linkedAccountIds: (dto.linked_account_ids ?? []).map(String),
    status,
    currentAmount,
    remainingAmount,
    completionPercentage,
    estimatedCompletionDate: dto.estimated_completion_date,
    createdAt: dto.created_at,
    updatedAt: dto.updated_at,
    completedAt: dto.completed_at,
    archivedAt: dto.archived_at,
    priority: toGoalPriority(priority),
    displayStatus: display.status,
  }
}

export function createGoalsRepository(api: ApiClient) {
  return {
    async list(
      organizationId: string,
      filters?: { includeArchived?: boolean },
    ): Promise<GoalListItemView[]> {
      const params = new URLSearchParams()
      if (filters?.includeArchived) {
        params.set('include_archived', 'true')
      }
      const qs = params.toString()
      const path = `/organizations/${organizationId}/goals${qs ? `?${qs}` : ''}`
      const dto = await api.get<GoalListDto>(path)
      return (dto.items ?? []).map(item => mapGoalDto(item))
    },

    async get(organizationId: string, goalId: string): Promise<GoalDetailView> {
      const dto = await api.get<GoalDto>(
        `/organizations/${organizationId}/goals/${goalId}`,
      )
      return mapGoalDto(dto)
    },

    async create(
      organizationId: string,
      input: CreateGoalInput,
    ): Promise<GoalDetailView> {
      const body: Record<string, unknown> = {
        name: input.name,
        target_amount: input.targetAmount,
        currency: input.currency,
        strategy: input.strategy,
        target_date: input.targetDate ?? null,
      }
      if (input.strategy === 'linked_accounts') {
        body.linked_account_ids = input.linkedAccountIds ?? []
      }
      else if (input.linkedAccountIds?.length) {
        body.linked_account_ids = input.linkedAccountIds
      }

      const dto = await api.post<GoalDto>(
        `/organizations/${organizationId}/goals`,
        body,
      )
      return mapGoalDto(dto)
    },

    async update(
      organizationId: string,
      goalId: string,
      input: UpdateGoalInput,
    ): Promise<GoalDetailView> {
      const body: Record<string, unknown> = {}
      if (input.name !== undefined) body.name = input.name
      if (input.targetAmount !== undefined) body.target_amount = input.targetAmount
      if (input.targetDate !== undefined) body.target_date = input.targetDate
      if (input.linkedAccountIds !== undefined) {
        body.linked_account_ids = input.linkedAccountIds
      }

      const dto = await api.patch<GoalDto>(
        `/organizations/${organizationId}/goals/${goalId}`,
        body,
      )
      return mapGoalDto(dto)
    },

    async archive(
      organizationId: string,
      goalId: string,
    ): Promise<GoalDetailView> {
      const dto = await api.post<GoalDto>(
        `/organizations/${organizationId}/goals/${goalId}/archive`,
        {},
      )
      return mapGoalDto(dto)
    },

    async updateManualProgress(
      organizationId: string,
      goalId: string,
      currentAmount: string,
    ): Promise<GoalDetailView> {
      const dto = await api.post<GoalDto>(
        `/organizations/${organizationId}/goals/${goalId}/manual-progress`,
        { current_amount: currentAmount },
      )
      return mapGoalDto(dto)
    },
  }
}

export type GoalsRepository = ReturnType<typeof createGoalsRepository>
