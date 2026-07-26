import type { CommitmentDetailView, CommitmentListItemView } from '~/types/commitments'
import { buildCommitmentPaymentDraft } from '~/utils/commitment-payment'
import { track } from '~/utils/track'

export function useCommitmentPayment() {
  const composer = useTransactionComposerStore()

  function openPayment(item: CommitmentListItemView | CommitmentDetailView) {
    track('commitment_payment_started', {
      commitment_type: item.debtType,
      source_screen: 'commitments',
    })
    composer.openWithDraft(buildCommitmentPaymentDraft(item), {
      label: 'Pago de obligación',
    })
  }

  return { openPayment }
}
