import { describe, expect, it } from 'vitest'
import { resolveSessionEntry } from '../../services/session-entry-resolver'

const orgA = { id: 'org-a' }
const orgB = { id: 'org-b' }

const incomplete = {
  hasPreferences: false,
  hasAccount: false,
  skippedAccount: false,
  markedComplete: false,
}

describe('resolveSessionEntry', () => {
  it('sends unauthenticated users to login', () => {
    expect(
      resolveSessionEntry({
        isAuthenticated: false,
        legalCompliant: null,
        memberships: [],
        currentOrganizationId: null,
        onboarding: null,
      }),
    ).toBe('/login')
  })

  it('sends non-compliant authenticated users to legal review before onboarding', () => {
    expect(
      resolveSessionEntry({
        isAuthenticated: true,
        legalCompliant: false,
        memberships: [],
        currentOrganizationId: null,
        onboarding: null,
      }),
    ).toBe('/legal/review')

    expect(
      resolveSessionEntry({
        isAuthenticated: true,
        legalCompliant: false,
        memberships: [orgA],
        currentOrganizationId: orgA.id,
        onboarding: {
          hasPreferences: true,
          hasAccount: true,
          skippedAccount: false,
          markedComplete: true,
        },
      }),
    ).toBe('/legal/review')
  })

  it('skips legal gate when compliance is unknown (null)', () => {
    expect(
      resolveSessionEntry({
        isAuthenticated: true,
        legalCompliant: null,
        memberships: [],
        currentOrganizationId: null,
        onboarding: null,
      }),
    ).toBe('/onboarding/organization')
  })

  it('sends authenticated users with zero memberships to organization onboarding', () => {
    expect(
      resolveSessionEntry({
        isAuthenticated: true,
        legalCompliant: true,
        memberships: [],
        currentOrganizationId: null,
        onboarding: null,
      }),
    ).toBe('/onboarding/organization')
  })

  it('sends multi-org users without selection to select-organization', () => {
    expect(
      resolveSessionEntry({
        isAuthenticated: true,
        legalCompliant: true,
        memberships: [orgA, orgB],
        currentOrganizationId: null,
        onboarding: incomplete,
      }),
    ).toBe('/select-organization')
  })

  it('treats a single membership as selected', () => {
    expect(
      resolveSessionEntry({
        isAuthenticated: true,
        legalCompliant: true,
        memberships: [orgA],
        currentOrganizationId: null,
        onboarding: incomplete,
      }),
    ).toBe('/onboarding/preferences')
  })

  it('routes to preferences when org is selected but prefs are missing', () => {
    expect(
      resolveSessionEntry({
        isAuthenticated: true,
        legalCompliant: true,
        memberships: [orgA],
        currentOrganizationId: orgA.id,
        onboarding: incomplete,
      }),
    ).toBe('/onboarding/preferences')
  })

  it('routes to account when prefs exist but account is missing and not skipped', () => {
    expect(
      resolveSessionEntry({
        isAuthenticated: true,
        legalCompliant: true,
        memberships: [orgA],
        currentOrganizationId: orgA.id,
        onboarding: {
          hasPreferences: true,
          hasAccount: false,
          skippedAccount: false,
          markedComplete: false,
        },
      }),
    ).toBe('/onboarding/account')
  })

  it('routes to complete when prefs + account/skip are done but not marked complete', () => {
    expect(
      resolveSessionEntry({
        isAuthenticated: true,
        legalCompliant: true,
        memberships: [orgA],
        currentOrganizationId: orgA.id,
        onboarding: {
          hasPreferences: true,
          hasAccount: true,
          skippedAccount: false,
          markedComplete: false,
        },
      }),
    ).toBe('/onboarding/complete')

    expect(
      resolveSessionEntry({
        isAuthenticated: true,
        legalCompliant: true,
        memberships: [orgA],
        currentOrganizationId: orgA.id,
        onboarding: {
          hasPreferences: true,
          hasAccount: false,
          skippedAccount: true,
          markedComplete: false,
        },
      }),
    ).toBe('/onboarding/complete')
  })

  it('routes to dashboard when onboarding is marked complete', () => {
    expect(
      resolveSessionEntry({
        isAuthenticated: true,
        legalCompliant: true,
        memberships: [orgA],
        currentOrganizationId: orgA.id,
        onboarding: {
          hasPreferences: true,
          hasAccount: true,
          skippedAccount: false,
          markedComplete: true,
        },
      }),
    ).toBe('/app/dashboard')
  })

  it('assumes preferences when onboarding snapshot is null but org is selected', () => {
    expect(
      resolveSessionEntry({
        isAuthenticated: true,
        legalCompliant: true,
        memberships: [orgA],
        currentOrganizationId: orgA.id,
        onboarding: null,
      }),
    ).toBe('/onboarding/preferences')
  })
})
