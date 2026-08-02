import type { ApiClient } from '~/lib/api/types'
import type {
  CreateFxTransferInput,
  CreateTransactionInput,
  FxTransferView,
  TransactionDetailView,
  TransactionEntryView,
  TransactionListItemView,
  TransactionListQuery,
  TransactionListResult,
  TransactionNameMaps,
  UpdateTransactionMetadataInput,
} from '~/types/transactions'
import { toApiCreateBody } from '~/utils/transaction-payload'
import type { TransactionType } from '~/utils/transaction-presentation'

interface TransactionEntryDto {
  id: string
  account_id: string
  amount: string | number
  currency: string
}

interface TransactionDto {
  id: string
  organization_id: string
  transaction_type: string
  description: string
  category_id: string | null
  occurred_at: string
  notes: string | null
  status: string
  entries: TransactionEntryDto[]
  created_by_user_id: string
  updated_by_user_id: string
  voided_by_user_id: string | null
  created_at: string
  updated_at: string
  voided_at: string | null
  source_account_id?: string | null
  destination_account_id?: string | null
  amount?: string | number | null
}

interface TransactionListDto {
  items: TransactionDto[]
  total: number
  limit: number
  offset: number
}

function toDecimalString(value: string | number | null | undefined): string {
  if (value == null) return '0.00'
  if (typeof value === 'number') return value.toFixed(2)
  const trimmed = String(value).trim()
  return trimmed || '0.00'
}

function primaryAccountId(dto: TransactionDto): string | null {
  if (dto.transaction_type === 'transfer') return dto.source_account_id ?? null
  if (dto.entries?.length) {
    // Prefer the account that matches the transaction direction for income/expense/adjustment
    if (dto.transaction_type === 'expense') {
      const debit = dto.entries.find(e => String(e.amount).trim().startsWith('-'))
      if (debit) return debit.account_id
    }
    if (dto.transaction_type === 'income' || dto.transaction_type === 'adjustment') {
      return dto.entries[0]?.account_id ?? null
    }
    return dto.entries[0]?.account_id ?? null
  }
  return null
}

function resolveCurrency(dto: TransactionDto, maps?: TransactionNameMaps): string {
  const fromEntry = dto.entries?.[0]?.currency
  if (fromEntry) return fromEntry
  const accountId = primaryAccountId(dto) ?? dto.source_account_id
  if (accountId && maps?.accounts?.has(accountId)) {
    return maps.accounts.get(accountId)!.currency
  }
  return 'MXN'
}

function resolveSignedAmount(dto: TransactionDto): string | null {
  if (dto.transaction_type === 'adjustment' && dto.entries?.length) {
    return toDecimalString(dto.entries[0].amount)
  }
  if (dto.amount != null) {
    const mag = toDecimalString(dto.amount)
    if (dto.transaction_type === 'expense') return mag.startsWith('-') ? mag : `-${mag.replace(/^[+-]/, '')}`
    if (dto.transaction_type === 'income') return mag.replace(/^[+-]/, '')
    return mag
  }
  return null
}

function mapEntry(
  dto: TransactionEntryDto,
  maps?: TransactionNameMaps,
): TransactionEntryView {
  return {
    id: dto.id,
    accountId: dto.account_id,
    accountName: maps?.accounts?.get(dto.account_id)?.name,
    amount: toDecimalString(dto.amount),
    currency: dto.currency,
  }
}

export function mapTransactionDto(
  dto: TransactionDto,
  maps?: TransactionNameMaps,
): TransactionDetailView {
  const accountId = primaryAccountId(dto)
  const category = dto.category_id ? maps?.categories?.get(dto.category_id) : undefined
  const categoryName = category
    ? (category.parentName ? `${category.parentName} / ${category.name}` : category.name)
    : null

  return {
    id: dto.id,
    organizationId: dto.organization_id,
    type: dto.transaction_type as TransactionType,
    description: dto.description,
    categoryId: dto.category_id,
    categoryName,
    occurredAt: dto.occurred_at,
    notes: dto.notes,
    status: dto.status,
    amount: toDecimalString(dto.amount ?? dto.entries?.[0]?.amount),
    currency: resolveCurrency(dto, maps),
    signedAmount: resolveSignedAmount(dto),
    sourceAccountId: dto.source_account_id ?? null,
    destinationAccountId: dto.destination_account_id ?? null,
    accountId,
    accountName: accountId ? maps?.accounts?.get(accountId)?.name ?? null : null,
    sourceAccountName: dto.source_account_id
      ? maps?.accounts?.get(dto.source_account_id)?.name ?? null
      : null,
    destinationAccountName: dto.destination_account_id
      ? maps?.accounts?.get(dto.destination_account_id)?.name ?? null
      : null,
    createdAt: dto.created_at,
    updatedAt: dto.updated_at,
    voidedAt: dto.voided_at,
    entries: (dto.entries ?? []).map(e => mapEntry(e, maps)),
    createdByUserId: dto.created_by_user_id,
    updatedByUserId: dto.updated_by_user_id,
    voidedByUserId: dto.voided_by_user_id,
  }
}

export function enrichTransactionItem(
  item: TransactionListItemView,
  maps: TransactionNameMaps,
): TransactionListItemView {
  const category = item.categoryId ? maps.categories?.get(item.categoryId) : undefined
  const categoryName = category
    ? (category.parentName ? `${category.parentName} / ${category.name}` : category.name)
    : item.categoryName

  return {
    ...item,
    categoryName,
    accountName: item.accountId
      ? maps.accounts?.get(item.accountId)?.name ?? item.accountName
      : item.accountName,
    sourceAccountName: item.sourceAccountId
      ? maps.accounts?.get(item.sourceAccountId)?.name ?? item.sourceAccountName
      : item.sourceAccountName,
    destinationAccountName: item.destinationAccountId
      ? maps.accounts?.get(item.destinationAccountId)?.name ?? item.destinationAccountName
      : item.destinationAccountName,
    currency: item.accountId && maps.accounts?.has(item.accountId)
      ? maps.accounts.get(item.accountId)!.currency
      : item.sourceAccountId && maps.accounts?.has(item.sourceAccountId)
        ? maps.accounts.get(item.sourceAccountId)!.currency
        : item.currency,
  }
}

export function createTransactionsRepository(api: ApiClient) {
  return {
    async list(
      organizationId: string,
      query: TransactionListQuery = {},
      maps?: TransactionNameMaps,
    ): Promise<TransactionListResult> {
      const params = new URLSearchParams()
      if (query.type) params.set('type', query.type)
      if (query.status) params.set('status', query.status)
      if (query.accountId) params.set('account_id', query.accountId)
      if (query.categoryId) params.set('category_id', query.categoryId)
      if (query.dateFrom) params.set('date_from', query.dateFrom)
      if (query.dateTo) params.set('date_to', query.dateTo)
      if (query.search) params.set('search', query.search)
      if (query.limit != null) params.set('limit', String(query.limit))
      if (query.offset != null) params.set('offset', String(query.offset))

      const qs = params.toString()
      const path = `/organizations/${organizationId}/transactions${qs ? `?${qs}` : ''}`
      const dto = await api.get<TransactionListDto>(path)
      return {
        items: (dto.items ?? []).map(item => mapTransactionDto(item, maps)),
        total: dto.total ?? 0,
        limit: dto.limit ?? query.limit ?? 50,
        offset: dto.offset ?? query.offset ?? 0,
      }
    },

    async get(
      organizationId: string,
      transactionId: string,
      maps?: TransactionNameMaps,
    ): Promise<TransactionDetailView> {
      const dto = await api.get<TransactionDto>(
        `/organizations/${organizationId}/transactions/${transactionId}`,
      )
      return mapTransactionDto(dto, maps)
    },

    async create(
      organizationId: string,
      input: CreateTransactionInput,
      idempotencyKey: string,
    ): Promise<TransactionDetailView> {
      const dto = await api.post<TransactionDto>(
        `/organizations/${organizationId}/transactions`,
        toApiCreateBody(input),
        { headers: { 'Idempotency-Key': idempotencyKey } },
      )
      return mapTransactionDto(dto)
    },

    async createFxTransfer(
      organizationId: string,
      input: CreateFxTransferInput,
      idempotencyKey: string,
    ): Promise<FxTransferView> {
      const body: Record<string, unknown> = {
        source_account_id: input.sourceAccountId,
        destination_account_id: input.destinationAccountId,
        source_amount: input.sourceAmount,
        destination_amount: input.destinationAmount,
        description: input.description,
        occurred_at: input.occurredAt,
        notes: input.notes ?? null,
      }
      if (input.feeAmount) body.fee_amount = input.feeAmount

      const dto = await api.post<{
        id: string
        source_account_id: string
        destination_account_id: string
        source_amount: string
        source_currency: string
        destination_amount: string
        destination_currency: string
        effective_exchange_rate: string
        fee_amount: string | null
        fee_currency: string | null
        occurred_at: string
        description: string
        notes: string | null
        source_transaction_id: string
        destination_transaction_id: string
        fee_transaction_id: string | null
      }>(
        `/organizations/${organizationId}/fx-transfers`,
        body,
        { headers: { 'Idempotency-Key': idempotencyKey } },
      )

      return {
        id: dto.id,
        sourceAccountId: dto.source_account_id,
        destinationAccountId: dto.destination_account_id,
        sourceAmount: toDecimalString(dto.source_amount),
        sourceCurrency: dto.source_currency,
        destinationAmount: toDecimalString(dto.destination_amount),
        destinationCurrency: dto.destination_currency,
        effectiveExchangeRate: String(dto.effective_exchange_rate),
        feeAmount: dto.fee_amount != null ? toDecimalString(dto.fee_amount) : null,
        feeCurrency: dto.fee_currency,
        occurredAt: dto.occurred_at,
        description: dto.description,
        notes: dto.notes,
        sourceTransactionId: dto.source_transaction_id,
        destinationTransactionId: dto.destination_transaction_id,
        feeTransactionId: dto.fee_transaction_id,
      }
    },

    async updateMetadata(
      organizationId: string,
      transactionId: string,
      input: UpdateTransactionMetadataInput,
    ): Promise<TransactionDetailView> {
      const body: Record<string, unknown> = {}
      if (input.description !== undefined) body.description = input.description
      if (input.notes !== undefined) body.notes = input.notes
      if (input.occurredAt !== undefined) body.occurred_at = input.occurredAt
      if (input.categoryId !== undefined) body.category_id = input.categoryId

      const dto = await api.patch<TransactionDto>(
        `/organizations/${organizationId}/transactions/${transactionId}`,
        body,
      )
      return mapTransactionDto(dto)
    },

    async void(
      organizationId: string,
      transactionId: string,
    ): Promise<TransactionDetailView> {
      const dto = await api.post<TransactionDto>(
        `/organizations/${organizationId}/transactions/${transactionId}/void`,
        {},
      )
      return mapTransactionDto(dto)
    },
  }
}

export type TransactionsRepository = ReturnType<typeof createTransactionsRepository>
