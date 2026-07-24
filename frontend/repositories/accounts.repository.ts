import type { ApiClient } from '~/lib/api/types'
import type { AccountSummary } from '~/types/domain'

export interface CreateAccountInput {
  name: string
  accountType: string
  currency: string
  openingBalance?: string
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
  opening_balance: string
  current_balance: string
  institution_name: string | null
  last_four: string | null
  is_active: boolean
}

interface AccountListDto {
  items: AccountDto[]
  total: number
}

function mapAccount(dto: AccountDto): AccountSummary {
  return {
    id: dto.id,
    organizationId: dto.organization_id,
    name: dto.name,
    accountType: dto.account_type,
    classification: dto.classification,
    currency: dto.currency,
    openingBalance: dto.opening_balance,
    currentBalance: dto.current_balance,
    institutionName: dto.institution_name,
    lastFour: dto.last_four,
    isActive: dto.is_active,
  }
}

export function createAccountsRepository(api: ApiClient) {
  return {
    async list(organizationId: string): Promise<AccountSummary[]> {
      const dto = await api.get<AccountListDto>(
        `/organizations/${organizationId}/accounts`,
      )
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
          institution_name: input.institutionName ?? null,
          last_four: input.lastFour ?? null,
        },
      )
      return mapAccount(dto)
    },
  }
}

export type AccountsRepository = ReturnType<typeof createAccountsRepository>
