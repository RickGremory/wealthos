import { describe, expect, it } from 'vitest'
import { resolveSessionEntry } from '../../services/session-entry-resolver'

describe('legal session gate', () => {
  it('prioritizes legal review over org onboarding', () => {
    expect(
      resolveSessionEntry({
        isAuthenticated: true,
        legalCompliant: false,
        memberships: [],
        currentOrganizationId: null,
        onboarding: null,
      }),
    ).toBe('/legal/review')
  })
})
