export interface UserSummary {
  id: string
  email: string
  displayName: string
  isActive: boolean
}

export interface OrganizationSummary {
  id: string
  name: string
  slug: string
  currency: string
  timezone: string
  locale: string
  role: string
}

export interface FeatureFlags {
  taxesMx: boolean
  recurringDetection: boolean
  advancedPayoff: boolean
  taxEvidence: boolean
  planning: boolean
  taxes: boolean
  debts: boolean
  goals: boolean
}

export interface TokenPayload {
  accessToken: string
  expiresIn: number
  tokenType?: string
}

export interface AccountSummary {
  id: string
  organizationId: string
  name: string
  accountType: string
  classification: 'asset' | 'liability' | string
  currency: string
  openingBalance: string
  currentBalance: string
  institutionName: string | null
  lastFour: string | null
  isActive: boolean
}
