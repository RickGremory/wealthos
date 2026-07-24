export type GoalStrategy = 'manual' | 'linked_accounts' | 'net_worth_percentage'

export type GoalStatus = 'active' | 'completed' | 'archived'

/** FE-only priority stored in preferences cookie. */
export type GoalPriority = 1 | 2 | 3

export type GoalDisplayStatus =
  | 'completed'
  | 'on_track'
  | 'behind'
  | 'paused'
  | 'active'

export interface GoalListItemView {
  id: string
  organizationId: string
  name: string
  targetAmount: string
  currency: string
  targetDate: string | null
  strategy: GoalStrategy
  linkedAccountIds: string[]
  status: GoalStatus
  currentAmount: string
  remainingAmount: string
  completionPercentage: string
  estimatedCompletionDate: string | null
  createdAt: string
  updatedAt: string
  completedAt: string | null
  archivedAt: string | null
  /** FE-only, from preferences. Default 2 (Media). */
  priority: GoalPriority
  displayStatus: GoalDisplayStatus
}

export type GoalDetailView = GoalListItemView

export interface GoalSummaryView {
  activeCount: number
  accumulatedSavings: string
  averageProgress: string
  nearestGoalName: string | null
  currency: string | null
}

export interface CreateGoalInput {
  name: string
  targetAmount: string
  currency: string
  strategy: GoalStrategy
  targetDate?: string | null
  linkedAccountIds?: string[]
}

export interface UpdateGoalInput {
  name?: string
  targetAmount?: string
  targetDate?: string | null
  linkedAccountIds?: string[]
}

export interface GoalTemplate {
  id: string
  name: string
  suggestedTargetAmount: string
  emoji: string
  strategyHint: GoalStrategy
  description: string
}

export interface CreateGoalFormModel {
  name: string
  targetAmount: string
  currency: string
  strategy: GoalStrategy
  targetDate: string
  linkedAccountIds: string[]
  priority: GoalPriority
  templateId: string | null
}

export interface UpdateGoalFormModel {
  name: string
  targetAmount: string
  targetDate: string
  linkedAccountIds: string[]
  priority: GoalPriority
}

export interface GoalAccountOption {
  id: string
  name: string
  currency: string
  currentBalance: string
  accountType: string
}
