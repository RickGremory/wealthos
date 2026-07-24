import type { FeatureFlags } from '~/types/domain'

const DEFAULT_FLAGS: FeatureFlags = {
  taxesMx: false,
  recurringDetection: false,
  advancedPayoff: false,
  taxEvidence: false,
  planning: true,
  taxes: true,
  debts: true,
  goals: true,
}

export function useFeatureFlags() {
  const config = useRuntimeConfig()
  const raw = (config.public.featureFlags ?? {}) as Partial<FeatureFlags>

  const flags = computed<FeatureFlags>(() => ({
    taxesMx: raw.taxesMx ?? DEFAULT_FLAGS.taxesMx,
    recurringDetection: raw.recurringDetection ?? DEFAULT_FLAGS.recurringDetection,
    advancedPayoff: raw.advancedPayoff ?? DEFAULT_FLAGS.advancedPayoff,
    taxEvidence: raw.taxEvidence ?? DEFAULT_FLAGS.taxEvidence,
    planning: raw.planning ?? DEFAULT_FLAGS.planning,
    taxes: raw.taxes ?? DEFAULT_FLAGS.taxes,
    debts: raw.debts ?? DEFAULT_FLAGS.debts,
    goals: raw.goals ?? DEFAULT_FLAGS.goals,
  }))

  function isEnabled(flag: keyof FeatureFlags): boolean {
    return flags.value[flag]
  }

  return { flags, isEnabled }
}
