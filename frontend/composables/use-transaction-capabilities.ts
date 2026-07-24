import { getAccountCapabilities } from '~/utils/transaction-capabilities'

export function useTransactionCapabilities() {
  return {
    getAccountCapabilities,
  }
}
