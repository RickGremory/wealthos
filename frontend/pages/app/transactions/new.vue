<script setup lang="ts">
import type { TransactionDuplicateDraft, TransactionType } from '~/types/transactions'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const route = useRoute()
const composer = useTransactionComposerStore()

function parsePrefillFromQuery(): Partial<TransactionDuplicateDraft> | null {
  const type = String(route.query.type ?? '')
  const destination = String(route.query.destination_account_id ?? '')
  const source = String(route.query.source ?? '')
  if (type !== 'transfer' && !destination) return null

  const draft: Partial<TransactionDuplicateDraft> = {
    type: (type as TransactionType) || 'transfer',
  }
  if (destination) draft.destinationAccountId = destination
  if (route.query.source_account_id) {
    draft.sourceAccountId = String(route.query.source_account_id)
  }
  if (route.query.amount) draft.amount = String(route.query.amount)
  if (route.query.description) draft.description = String(route.query.description)
  if (source === 'commitment') {
    // label applied via openWithDraft options below
  }
  return draft
}

onMounted(() => {
  const draft = parsePrefillFromQuery()
  if (draft && (draft.destinationAccountId || draft.type === 'transfer')) {
    const fromCommitment = String(route.query.source ?? '') === 'commitment'
    composer.openWithDraft(draft, {
      label: fromCommitment ? 'Pago de obligación' : undefined,
    })
  }
  else {
    composer.openCreate('expense')
  }
  void navigateTo('/app/transactions', { replace: true })
})
</script>

<template>
  <div data-testid="transactions-new-redirect">
    <UiSkeleton style="height: 8rem" />
  </div>
</template>
