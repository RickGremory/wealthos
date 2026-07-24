import {
  presentTransaction,
  displayAmountMagnitude,
  presentTransactionType,
  presentTransactionStatus,
} from '~/utils/transaction-presentation'

export function useTransactionPresentation() {
  return {
    presentTransaction,
    displayAmountMagnitude,
    presentTransactionType,
    presentTransactionStatus,
  }
}
