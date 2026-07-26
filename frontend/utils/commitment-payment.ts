import type { CommitmentDetailView, CommitmentListItemView } from '~/types/commitments'
import type { TransactionDuplicateDraft } from '~/types/transactions'

/** Suggested payment amount: scheduled → minimum → nextAction.amount → null */
export function suggestedCommitmentPaymentAmount(
  item: CommitmentListItemView | CommitmentDetailView,
): string | null {
  if (item.scheduledPayment) return item.scheduledPayment
  if (item.minimumPayment) return item.minimumPayment
  if (item.nextAction?.amount) return item.nextAction.amount
  return null
}

export function buildCommitmentPaymentDraft(
  item: CommitmentListItemView | CommitmentDetailView,
): TransactionDuplicateDraft {
  const amount = suggestedCommitmentPaymentAmount(item) ?? undefined
  return {
    type: 'transfer',
    destinationAccountId: item.accountId,
    description: `Pago de ${item.name}`,
    amount,
    notes: item.creditor ? `Acreedor: ${item.creditor}` : undefined,
  }
}

export function commitmentPaymentQuery(item: CommitmentListItemView | CommitmentDetailView): Record<string, string> {
  const q: Record<string, string> = {
    type: 'transfer',
    destination_account_id: item.accountId,
    source: 'commitment',
    commitment_id: item.id,
  }
  const amount = suggestedCommitmentPaymentAmount(item)
  if (amount) q.amount = amount
  q.description = `Pago de ${item.name}`
  return q
}
