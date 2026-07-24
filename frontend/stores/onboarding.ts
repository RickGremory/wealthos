import { defineStore } from 'pinia'

export interface OnboardingOrgProgress {
  hasPreferences: boolean
  preferences: string[]
  skippedAccount: boolean
  markedComplete: boolean
}

type OnboardingProgressMap = Record<string, OnboardingOrgProgress>

function emptyProgress(): OnboardingOrgProgress {
  return {
    hasPreferences: false,
    preferences: [],
    skippedAccount: false,
    markedComplete: false,
  }
}

export const useOnboardingStore = defineStore('onboarding', () => {
  const progressCookie = useCookie<OnboardingProgressMap>('wealthos_onboarding_progress', {
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 365,
    default: () => ({}),
  })

  const currentOrgId = ref<string | null>(null)
  const progress = ref<OnboardingOrgProgress>(emptyProgress())

  function getProgress(orgId: string): OnboardingOrgProgress {
    return progressCookie.value?.[orgId] ?? emptyProgress()
  }

  function writeProgress(orgId: string, next: OnboardingOrgProgress) {
    progressCookie.value = {
      ...(progressCookie.value ?? {}),
      [orgId]: next,
    }
    if (currentOrgId.value === orgId) {
      progress.value = next
    }
  }

  function loadProgress(orgId: string) {
    currentOrgId.value = orgId
    progress.value = getProgress(orgId)
    return progress.value
  }

  function savePreferences(orgId: string, intents: string[]) {
    const current = getProgress(orgId)
    writeProgress(orgId, {
      ...current,
      hasPreferences: true,
      preferences: [...intents],
    })
  }

  function skipAccount(orgId: string) {
    const current = getProgress(orgId)
    writeProgress(orgId, {
      ...current,
      skippedAccount: true,
    })
  }

  function markComplete(orgId: string) {
    const current = getProgress(orgId)
    writeProgress(orgId, {
      ...current,
      markedComplete: true,
    })
  }

  function clear() {
    currentOrgId.value = null
    progress.value = emptyProgress()
  }

  return {
    currentOrgId,
    progress,
    getProgress,
    loadProgress,
    savePreferences,
    skipAccount,
    markComplete,
    clear,
  }
})
