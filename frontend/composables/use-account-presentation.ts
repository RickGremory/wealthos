import {
  ACCOUNT_GROUP_LABELS,
  ACCOUNT_GROUP_ORDER,
  ACCOUNT_TYPE_OPTIONS,
  getAccountTypeOption,
  presentAccount,
  toOpeningBalancePayload,
  type AccountPresentationInput,
} from '~/utils/account-type-mapper'

/**
 * Thin wrapper around account-type-mapper for Vue consumers.
 * Prefer this composable in components; keep mapper pure for tests/onboarding.
 */
export function useAccountPresentation() {
  function present(input: AccountPresentationInput) {
    return presentAccount(input)
  }

  function balanceLabelFor(type: string): string {
    return getAccountTypeOption(type).balanceLabel
  }

  function typeOptions() {
    return ACCOUNT_TYPE_OPTIONS
  }

  function openingBalancePayload(type: string, amount: string): string {
    return toOpeningBalancePayload(type, amount)
  }

  return {
    present,
    balanceLabelFor,
    typeOptions,
    openingBalancePayload,
    ACCOUNT_TYPE_OPTIONS,
    ACCOUNT_GROUP_LABELS,
    ACCOUNT_GROUP_ORDER,
    getAccountTypeOption,
    presentAccount,
    toOpeningBalancePayload,
  }
}
