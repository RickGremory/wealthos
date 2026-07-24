import { defineStore } from 'pinia'
import type {
  TransactionDuplicateDraft,
  TransactionListItemView,
  TransactionType,
} from '~/types/transactions'
import { displayAmountMagnitude } from '~/utils/transaction-presentation'

export const useTransactionComposerStore = defineStore('transaction-composer', () => {
  const open = ref(false)
  const mode = ref<'create' | 'duplicate'>('create')
  const initialType = ref<TransactionType>('expense')
  const duplicateDraft = ref<Partial<TransactionDuplicateDraft> | null>(null)

  function openCreate(type: TransactionType = 'expense') {
    mode.value = 'create'
    initialType.value = type
    duplicateDraft.value = null
    open.value = true
  }

  function openDuplicate(tx: TransactionListItemView) {
    mode.value = 'duplicate'
    initialType.value = (tx.type as TransactionType) || 'expense'
    duplicateDraft.value = {
      type: tx.type as TransactionType,
      amount: displayAmountMagnitude(tx.amount),
      description: tx.description,
      notes: tx.notes ?? '',
      accountId: tx.accountId ?? undefined,
      categoryId: tx.categoryId ?? undefined,
      sourceAccountId: tx.sourceAccountId ?? undefined,
      destinationAccountId: tx.destinationAccountId ?? undefined,
      signedAmount: tx.signedAmount ?? undefined,
    }
    open.value = true
  }

  function close() {
    open.value = false
    mode.value = 'create'
    duplicateDraft.value = null
  }

  return {
    open,
    mode,
    initialType,
    duplicateDraft,
    openCreate,
    openDuplicate,
    close,
  }
})
