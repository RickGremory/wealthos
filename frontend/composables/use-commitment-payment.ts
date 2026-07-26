import type { CommitmentDetailView, CommitmentListItemView } from '~/types/commitments'
import { buildCommitmentPaymentDraft } from '~/utils/commitment-payment'

export function useCommitmentPayment() {
  const composer = useTransactionComposerStore()

  function openPayment(item: CommitmentListItemView | CommitmentDetailView) {
    composer.openWithDraft(buildCommitmentPaymentDraft(item), {
      label: 'Pago de obligación',
    })
  }

  return { openPayment }
}
