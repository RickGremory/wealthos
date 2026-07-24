import type { ApiClient } from '~/lib/api/types'
import type { OrganizationSummary } from '~/types/domain'

export interface CreateOrganizationInput {
  name: string
  slug: string
  currency?: string
  timezone?: string
  locale?: string
}

interface UserOrganizationItemDto {
  id: string
  name: string
  slug: string
  currency: string
  timezone: string
  locale: string
  role: string
}

interface UserOrganizationListDto {
  items: UserOrganizationItemDto[]
  total: number
}

interface OrganizationResponseDto {
  id: string
  name: string
  slug: string
  currency: string
  timezone: string
  locale: string
  created_at?: string
  updated_at?: string
}

function mapOrg(dto: UserOrganizationItemDto): OrganizationSummary {
  return {
    id: dto.id,
    name: dto.name,
    slug: dto.slug,
    currency: dto.currency,
    timezone: dto.timezone,
    locale: dto.locale,
    role: dto.role,
  }
}

function mapCreated(dto: OrganizationResponseDto): Omit<OrganizationSummary, 'role'> {
  return {
    id: dto.id,
    name: dto.name,
    slug: dto.slug,
    currency: dto.currency,
    timezone: dto.timezone,
    locale: dto.locale,
  }
}

export function createOrganizationsRepository(api: ApiClient) {
  return {
    async listMemberships(): Promise<OrganizationSummary[]> {
      const dto = await api.get<UserOrganizationListDto>('/me/organizations')
      return (dto.items ?? []).map(mapOrg)
    },

    async create(input: CreateOrganizationInput): Promise<Omit<OrganizationSummary, 'role'>> {
      const dto = await api.post<OrganizationResponseDto>('/organizations', {
        name: input.name,
        slug: input.slug,
        currency: input.currency ?? 'MXN',
        timezone: input.timezone ?? 'America/Cancun',
        locale: input.locale ?? 'es-MX',
      })
      return mapCreated(dto)
    },
  }
}

export type OrganizationsRepository = ReturnType<typeof createOrganizationsRepository>
