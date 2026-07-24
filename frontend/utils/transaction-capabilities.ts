/**
 * Which transaction operations each account type supports in V1.
 */

import { normalizeAccountType, type BackendAccountType } from '~/utils/account-type-mapper'

export interface TransactionAccountCapabilities {
  canReceiveIncome: boolean
  canPayExpense: boolean
  canTransferFrom: boolean
  canTransferTo: boolean
  canAdjust: boolean
}

const CAPABILITIES: Record<BackendAccountType, TransactionAccountCapabilities> = {
  checking: {
    canReceiveIncome: true,
    canPayExpense: true,
    canTransferFrom: true,
    canTransferTo: true,
    canAdjust: true,
  },
  savings: {
    canReceiveIncome: true,
    canPayExpense: true,
    canTransferFrom: true,
    canTransferTo: true,
    canAdjust: true,
  },
  cash: {
    canReceiveIncome: true,
    canPayExpense: true,
    canTransferFrom: true,
    canTransferTo: true,
    canAdjust: true,
  },
  digital_wallet: {
    canReceiveIncome: true,
    canPayExpense: true,
    canTransferFrom: true,
    canTransferTo: true,
    canAdjust: true,
  },
  investment: {
    canReceiveIncome: true,
    canPayExpense: false,
    canTransferFrom: true,
    canTransferTo: true,
    canAdjust: true,
  },
  credit_card: {
    canReceiveIncome: false,
    canPayExpense: true,
    canTransferFrom: false,
    canTransferTo: true,
    canAdjust: true,
  },
  loan: {
    canReceiveIncome: false,
    canPayExpense: false,
    canTransferFrom: false,
    canTransferTo: true,
    canAdjust: true,
  },
  other: {
    canReceiveIncome: true,
    canPayExpense: true,
    canTransferFrom: true,
    canTransferTo: true,
    canAdjust: true,
  },
}

export function getAccountCapabilities(
  accountType: string,
): TransactionAccountCapabilities {
  return CAPABILITIES[normalizeAccountType(accountType)]
}

