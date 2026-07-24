export type EntryDestination =
  | '/login'
  | '/legal/review'
  | '/onboarding/organization'
  | '/select-organization'
  | '/onboarding/preferences'
  | '/onboarding/account'
  | '/onboarding/complete'
  | '/app/dashboard'

export function resolveSessionEntry(input: {
  isAuthenticated: boolean
  /** null = unknown/skip (e.g. guests or when status not fetched) */
  legalCompliant: boolean | null
  memberships: Array<{ id: string }>
  currentOrganizationId: string | null
  onboarding: {
    hasPreferences: boolean
    hasAccount: boolean
    skippedAccount: boolean
    markedComplete: boolean
  } | null
}): EntryDestination {
  if (!input.isAuthenticated) {
    return '/login'
  }

  if (input.legalCompliant === false) {
    return '/legal/review'
  }

  const { memberships, currentOrganizationId, onboarding } = input

  if (memberships.length === 0) {
    return '/onboarding/organization'
  }

  const effectiveOrgId =
    currentOrganizationId
    ?? (memberships.length === 1 ? memberships[0]!.id : null)

  if (!effectiveOrgId) {
    return '/select-organization'
  }

  if (!onboarding) {
    return '/onboarding/preferences'
  }

  if (onboarding.markedComplete) {
    return '/app/dashboard'
  }

  if (!onboarding.hasPreferences) {
    return '/onboarding/preferences'
  }

  if (!onboarding.hasAccount && !onboarding.skippedAccount) {
    return '/onboarding/account'
  }

  return '/onboarding/complete'
}
