import type {
  QuickPeriod,
  TransactionFiltersState,
  TransactionStatusFilter,
  TransactionTypeFilter,
} from '~/utils/transaction-filters'
import type {
  PresentationSign,
  TransactionStatus,
  TransactionType,
} from '~/utils/transaction-presentation'

export type {
  QuickPeriod,
  TransactionFiltersState,
  TransactionStatusFilter,
  TransactionTypeFilter,
  PresentationSign,
  TransactionStatus,
  TransactionType,
}

export interface TransactionEntryView {
  id: string
  accountId: string
  accountName?: string
  amount: string
  currency: string
}

export interface TransactionListItemView {
  id: string
  organizationId: string
  type: TransactionType | string
  description: string
  categoryId: string | null
  categoryName?: string | null
  occurredAt: string
  notes: string | null
  status: TransactionStatus | string
  amount: string
  currency: string
  signedAmount?: string | null
  sourceAccountId?: string | null
  destinationAccountId?: string | null
  accountId?: string | null
  accountName?: string | null
  sourceAccountName?: string | null
  destinationAccountName?: string | null
  createdAt: string
  updatedAt: string
  voidedAt: string | null
}

export interface TransactionDetailView extends TransactionListItemView {
  entries: TransactionEntryView[]
  createdByUserId: string
  updatedByUserId: string
  voidedByUserId: string | null
}

export interface TransactionListResult {
  items: TransactionListItemView[]
  total: number
  limit: number
  offset: number
}

export interface TransactionSourceInput {
  type: 'recurring_occurrence'
  occurrenceKey: string
  relatedResourceType?: 'recurring_rule' | null
  relatedResourceId?: string | null
}

export interface CreateIncomeTransactionInput {
  transactionType: 'income'
  accountId: string
  categoryId: string
  amount: string
  description: string
  occurredAt: string
  notes?: string | null
  source?: TransactionSourceInput | null
}

export interface CreateExpenseTransactionInput {
  transactionType: 'expense'
  accountId: string
  categoryId: string
  amount: string
  description: string
  occurredAt: string
  notes?: string | null
  source?: TransactionSourceInput | null
}

export interface CreateTransferTransactionInput {
  transactionType: 'transfer'
  sourceAccountId: string
  destinationAccountId: string
  amount: string
  description: string
  occurredAt: string
  notes?: string | null
  source?: TransactionSourceInput | null
}

export interface CreateAdjustmentTransactionInput {
  transactionType: 'adjustment'
  accountId: string
  amount: string
  description: string
  occurredAt: string
  categoryId?: string | null
  notes?: string | null
  source?: TransactionSourceInput | null
}

export type CreateTransactionInput =
  | CreateIncomeTransactionInput
  | CreateExpenseTransactionInput
  | CreateTransferTransactionInput
  | CreateAdjustmentTransactionInput

export interface UpdateTransactionMetadataInput {
  description?: string | null
  notes?: string | null
  occurredAt?: string | null
  categoryId?: string | null
}

export interface TransactionListQuery {
  type?: string | null
  status?: string | null
  accountId?: string | null
  categoryId?: string | null
  dateFrom?: string | null
  dateTo?: string | null
  search?: string | null
  limit?: number
  offset?: number
}

export interface TransactionFormModel {
  type: TransactionType
  amount: string
  description: string
  notes: string
  occurredDate: string
  accountId: string
  categoryId: string
  sourceAccountId: string
  destinationAccountId: string
  /** Real balance entered by user for adjustment UX */
  realBalance: string
  /** Sprint 9.6: cross-currency conversion flow */
  fxConversion: boolean
  /** Amount credited on destination account (FX only) */
  destinationAmount: string
  /** Optional fee charged on source account (FX only) */
  feeAmount: string
}

export interface CreateFxTransferInput {
  sourceAccountId: string
  destinationAccountId: string
  sourceAmount: string
  destinationAmount: string
  description: string
  occurredAt: string
  feeAmount?: string | null
  notes?: string | null
}

export interface FxTransferView {
  id: string
  sourceAccountId: string
  destinationAccountId: string
  sourceAmount: string
  sourceCurrency: string
  destinationAmount: string
  destinationCurrency: string
  effectiveExchangeRate: string
  feeAmount: string | null
  feeCurrency: string | null
  occurredAt: string
  description: string
  notes: string | null
  sourceTransactionId: string
  destinationTransactionId: string
  feeTransactionId: string | null
}

export interface TransactionDuplicateDraft {
  type?: TransactionType
  amount?: string
  description?: string
  notes?: string
  accountId?: string
  categoryId?: string
  sourceAccountId?: string
  destinationAccountId?: string
  realBalance?: string
  signedAmount?: string
  /** Local calendar date YYYY-MM-DD */
  occurredDate?: string
}

export interface TransactionNameMaps {
  accounts?: Map<string, { name: string, currency: string, accountType?: string }>
  categories?: Map<string, { name: string, parentName?: string | null }>
}
