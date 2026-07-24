import type { ApiClient } from '~/lib/api/types'
import type { OrganizationSummary } from '~/types/domain'

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

export function createOrganizationsRepository(api: ApiClient) {
  return {
    async listMemberships(): Promise<OrganizationSummary[]> {
      const dto = await api.get<UserOrganizationListDto>('/me/organizations')
      return (dto.items ?? []).map(mapOrg)
    },
  }
}

export type OrganizationsRepository = ReturnType<typeof createOrganizationsRepository>
