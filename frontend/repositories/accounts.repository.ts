import type { ApiClient } from '~/lib/api/types'
import type { AccountSummary } from '~/types/domain'
import type { UpdateAccountInput } from '~/types/accounts'

export interface CreateAccountInput {
  name: string
  accountType: string
  currency: string
  openingBalance?: string
  openingBalanceDate?: string | null
  institutionName?: string | null
  lastFour?: string | null
}

interface AccountDto {
  id: string
  organization_id: string
  name: string
  account_type: string
  classification: string
  currency: string
  opening_balance: string | number
  current_balance: string | number
  institution_name: string | null
  last_four: string | null
  is_active: boolean
  created_at?: string
  updated_at?: string
  archived_at?: string | null
}

interface AccountListDto {
  items: AccountDto[]
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

function mapAccount(dto: AccountDto): AccountSummary {
  return {
    id: dto.id,
    organizationId: dto.organization_id,
    name: dto.name,
    accountType: dto.account_type,
    classification: dto.classification,
    currency: dto.currency,
    openingBalance: toDecimalString(dto.opening_balance),
    currentBalance: toDecimalString(dto.current_balance),
    institutionName: dto.institution_name,
    lastFour: dto.last_four,
    isActive: dto.is_active,
    createdAt: dto.created_at,
    updatedAt: dto.updated_at,
    archivedAt: dto.archived_at ?? null,
  }
}

export function createAccountsRepository(api: ApiClient) {
  return {
    async list(
      organizationId: string,
      filters?: { includeArchived?: boolean },
    ): Promise<AccountSummary[]> {
      const params = new URLSearchParams()
      if (filters?.includeArchived) {
        params.set('include_archived', 'true')
      }
      const qs = params.toString()
      const path = `/organizations/${organizationId}/accounts${qs ? `?${qs}` : ''}`
      const dto = await api.get<AccountListDto>(path)
      return (dto.items ?? []).map(mapAccount)
    },

    async get(organizationId: string, accountId: string): Promise<AccountSummary> {
      const dto = await api.get<AccountDto>(
        `/organizations/${organizationId}/accounts/${accountId}`,
      )
      return mapAccount(dto)
    },

    async create(
      organizationId: string,
      input: CreateAccountInput,
    ): Promise<AccountSummary> {
      const dto = await api.post<AccountDto>(
        `/organizations/${organizationId}/accounts`,
        {
          name: input.name,
          account_type: input.accountType,
          currency: input.currency,
          opening_balance: input.openingBalance ?? '0.00',
          opening_balance_date: input.openingBalanceDate ?? null,
          institution_name: input.institutionName ?? null,
          last_four: input.lastFour ?? null,
        },
      )
      return mapAccount(dto)
    },

    async update(
      organizationId: string,
      accountId: string,
      input: UpdateAccountInput,
    ): Promise<AccountSummary> {
      const body: Record<string, unknown> = {}
      if (input.name !== undefined) body.name = input.name
      if (input.institutionName !== undefined) {
        body.institution_name = input.institutionName
      }
      if (input.lastFour !== undefined) body.last_four = input.lastFour

      const dto = await api.patch<AccountDto>(
        `/organizations/${organizationId}/accounts/${accountId}`,
        body,
      )
      return mapAccount(dto)
    },

    async archive(
      organizationId: string,
      accountId: string,
    ): Promise<AccountSummary> {
      const dto = await api.post<AccountDto>(
        `/organizations/${organizationId}/accounts/${accountId}/archive`,
        {},
      )
      return mapAccount(dto)
    },
  }
}

export type AccountsRepository = ReturnType<typeof createAccountsRepository>
