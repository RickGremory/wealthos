import type { ApiClient } from '~/lib/api/types'
import type { TokenPayload, UserSummary } from '~/types/domain'

export interface RegisterInput {
  email: string
  password: string
  displayName: string
  organizationName: string
  currency?: string
  timezone?: string
  locale?: string
}

export interface LoginInput {
  email: string
  password: string
}

interface TokenResponseDto {
  access_token: string
  expires_in: number
  token_type?: string
}

interface CurrentUserDto {
  id: string
  email: string
  display_name: string
  is_active: boolean
}

function mapToken(dto: TokenResponseDto): TokenPayload {
  return {
    accessToken: dto.access_token,
    expiresIn: dto.expires_in,
    tokenType: dto.token_type,
  }
}

function mapUser(dto: CurrentUserDto): UserSummary {
  return {
    id: dto.id,
    email: dto.email,
    displayName: dto.display_name,
    isActive: dto.is_active,
  }
}

export function createAuthRepository(api: ApiClient) {
  return {
    async register(input: RegisterInput): Promise<TokenPayload> {
      const dto = await api.post<TokenResponseDto>(
        '/auth/register',
        {
          email: input.email,
          password: input.password,
          display_name: input.displayName,
          organization_name: input.organizationName,
          currency: input.currency ?? 'MXN',
          timezone: input.timezone ?? 'America/Cancun',
          locale: input.locale ?? 'es-MX',
        },
        { skipAuth: true },
      )
      return mapToken(dto)
    },

    async login(input: LoginInput): Promise<TokenPayload> {
      const body = new URLSearchParams()
      body.set('username', input.email)
      body.set('password', input.password)
      body.set('grant_type', 'password')

      const dto = await api.post<TokenResponseDto>('/auth/login', body, {
        skipAuth: true,
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })
      return mapToken(dto)
    },

    async me(): Promise<UserSummary> {
      const dto = await api.get<CurrentUserDto>('/auth/me')
      return mapUser(dto)
    },
  }
}

export type AuthRepository = ReturnType<typeof createAuthRepository>
