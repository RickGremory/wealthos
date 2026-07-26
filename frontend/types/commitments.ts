export type CommitmentType =
  | 'credit_card'
  | 'mortgage'
  | 'auto_loan'
  | 'personal_loan'
  | 'business_loan'
  | 'student_loan'
  | 'line_of_credit'
  | 'family_loan'
  | 'installment_plan'
  | 'other'

export type CommitmentStatus =
  | 'active'
  | 'paused'
  | 'defaulted'
  | 'closed'
  | 'archived'

export type CommitmentDisplayStatus =
  | 'active'
  | 'due_soon'
  | 'overdue'
  | 'settled'
  | 'paid_off'
  | 'paused'
  | 'defaulted'
  | 'archived'

export type CommitmentPriority = 'high' | 'medium' | 'low'

export type PaymentStrategy =
  | 'avalanche'
  | 'snowball'
  | 'minimum_only'
  | 'manual'

export type CommitmentNextActionType =
  | 'pay_overdue'
  | 'pay_minimum'
  | 'pay_priority_debt'
  | 'configure_payment'
  | 'configure_interest_rate'
  | 'review_paused'
  | 'no_action_required'

export interface CommitmentNextActionView {
  type: CommitmentNextActionType
  reasonCode: string
  amount: string | null
  dueDate: string | null
}

export interface CommitmentListItemView {
  id: string
  organizationId: string
  accountId: string
  name: string
  debtType: CommitmentType
  creditor: string | null
  currency: string
  priority: CommitmentPriority
  interestRate: string | null
  minimumPayment: string | null
  scheduledPayment: string | null
  creditLimit: string | null
  originalAmount: string | null
  maturityDate: string | null
  dueDay: number | null
  statementDay: number | null
  status: CommitmentStatus
  displayStatus: CommitmentDisplayStatus
  behavior: string | null
  notes: string | null
  version: number
  currentBalance: string
  nextDueDate: string | null
  daysUntilDue: number | null
  utilizationPercentage: string | null
  nextAction: CommitmentNextActionView | null
  createdAt: string
  updatedAt: string
  closedAt: string | null
  archivedAt: string | null
}

export type CommitmentDetailView = CommitmentListItemView

export interface CommitmentCurrencyGroupView {
  currency: string
  totalDebt: string
  totalMinimumPayments: string
  weightedAverageRate: string
  activeDebtCount: number
  highestInterestDebtId: string | null
  highestInterestRate: string | null
}

export interface CommitmentUpcomingDueView {
  commitmentId: string
  name: string
  currency: string
  dueDate: string
  daysUntilDue: number
  amount: string | null
}

export interface CommitmentSummaryView {
  groups: CommitmentCurrencyGroupView[]
  activeCommitments: number
  commitmentsNeedingAttention: number
  nextDue: CommitmentUpcomingDueView | null
}

export interface StrategyRankingItemView {
  position: number
  commitmentId: string
  name: string
  reasonCode: string
  eligible: boolean
}

export interface CommitmentStrategyView {
  status: string
  strategy: PaymentStrategy
  generatedAt: string
  summary: {
    activeCommitments: number
    totalBalance: string
    currency: string
  } | null
  nextAction: {
    type: string
    commitmentId: string | null
    amount: string | null
    dueDate: string | null
    reasonCode: string
  } | null
  ranking: StrategyRankingItemView[]
  warnings: string[]
  excludedCommitments: number
}

export interface CreateCommitmentInput {
  accountId: string
  name: string
  debtType: CommitmentType
  creditor?: string | null
  priority?: CommitmentPriority
  interestRate?: string | null
  minimumPayment?: string | null
  scheduledPayment?: string | null
  creditLimit?: string | null
  originalAmount?: string | null
  maturityDate?: string | null
  dueDay?: number | null
  statementDay?: number | null
  notes?: string | null
}

export interface UpdateCommitmentInput {
  name?: string
  creditor?: string | null
  priority?: CommitmentPriority
  interestRate?: string | null
  minimumPayment?: string | null
  scheduledPayment?: string | null
  creditLimit?: string | null
  maturityDate?: string | null
  dueDay?: number | null
  statementDay?: number | null
  notes?: string | null
  version: number
}

export interface CreateCommitmentFormModel {
  name: string
  debtType: CommitmentType
  creditor: string
  priority: CommitmentPriority
  accountId: string
  createAccountInline: boolean
  newAccountName: string
  newAccountType: 'credit_card' | 'loan'
  newAccountOpeningBalance: string
  currency: string
  interestRate: string
  minimumPayment: string
  scheduledPayment: string
  creditLimit: string
  dueDay: string
  statementDay: string
  notes: string
}

export interface UpdateCommitmentFormModel {
  name: string
  creditor: string
  priority: CommitmentPriority
  interestRate: string
  minimumPayment: string
  scheduledPayment: string
  creditLimit: string
  dueDay: string
  statementDay: string
  notes: string
  version: number
}

export interface CommitmentAccountOption {
  id: string
  name: string
  currency: string
  currentBalance: string
  accountType: string
  classification: string
}

export type CommitmentStatusFilter =
  | 'all'
  | 'active'
  | 'attention'
  | 'paused'
  | 'closed'
  | 'archived'
